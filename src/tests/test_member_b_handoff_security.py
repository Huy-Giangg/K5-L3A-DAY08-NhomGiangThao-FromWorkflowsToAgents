"""Test thành viên B: handoff thực, PII, approval, crash/resume và retry đồng thời.

Khung do Antigravity đề xuất; Codex chỉnh API, fixture và bổ sung nghiệm thu thực.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import sqlite3
from typing import Any

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.handoff import ALLOWED_FIELDS, FACT_KEYS
from lab8.schemas import Budget
from lab8.shapes import orchestrator


def assert_one_effect(path: Path, claim_id: str) -> None:
    conn = connect(path)
    try:
        row = get_refund(conn, claim_id)
        assert row is not None
        assert row["idempotency_key"] == f"refund:{claim_id}"
        assert row["amount_vnd"] == 35000
        assert committed_audit_count(conn, claim_id) == 1
        count = conn.execute(
            "SELECT COUNT(*) FROM refund_ledger WHERE claim_id = ?", (claim_id,),
        ).fetchone()[0]
        assert count == 1
    finally:
        conn.close()


def test_handoff_and_trace_omit_actual_secrets_and_pii(
    public_db: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    conn = connect(public_db)
    try:
        claim = conn.execute("SELECT * FROM claims WHERE claim_id='C-001'").fetchone()
        order = conn.execute(
            "SELECT phone,address,item_name,internal_note FROM orders WHERE order_id=?",
            (claim["order_id"],),
        ).fetchone()
        sensitive = [claim["parent_secret"], *dict(order).values(),
                     *json.loads(claim["raw_headers_json"]).values()]
    finally:
        conn.close()
    original = orchestrator.run_readonly_investigators
    captured: list[dict[str, Any]] = []

    def spy(conn: sqlite3.Connection, budget: Budget, handoff: dict[str, Any],
            principal_id: str) -> dict[str, Any]:
        captured.append(json.loads(json.dumps(handoff)))
        return original(conn, budget, handoff, principal_id)

    monkeypatch.setattr(orchestrator, "run_readonly_investigators", spy)
    result = orchestrator.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert len(captured) == 1
    packet = captured[0]
    assert set(packet) <= ALLOWED_FIELDS
    assert set(packet["facts"]) <= FACT_KEYS
    assert packet["facts"] == {}
    assert packet["allowed_tools"] == ["lookup_order", "lookup_policy", "compute_compensation"]
    trace = Path(result.trace_path).read_text(encoding="utf-8")
    output = capsys.readouterr()
    blob = trace + json.dumps(captured, ensure_ascii=False) + output.out + output.err
    for value in sensitive:
        if value:
            assert str(value) not in blob
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in blob
    assert "raw_headers" not in blob


@pytest.mark.parametrize("claim_id,status", [
    ("UNKNOWN", "failed"), ("C-004", "needs_info"),
    ("C-005", "escalated"), ("C-002", "denied"),
])
def test_early_returns_have_fresh_contract_trace(
    public_db: Path, claim_id: str, status: str,
) -> None:
    result = orchestrator.run_claim(claim_id, seed=22, store_path=str(public_db))
    assert result.status == status
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert body["run_id"] == result.run_id
    assert isinstance(body["events"], list)


@pytest.mark.parametrize("claim_id,status,proposal,paid", [
    ("C-013", "denied", 35000, 0), ("C-014", "resolved", 150000, 120000),
])
def test_full_quote_is_kept_when_host_applies_order_cap(
    public_db: Path, claim_id: str, status: str, proposal: int, paid: int,
) -> None:
    result = orchestrator.run_claim(claim_id, seed=11, store_path=str(public_db))
    assert result.status == status
    assert result.proposal_amount == proposal
    assert sum(row["amount_vnd"] for row in result.refund_effects) == paid


def test_borrowed_approval_cannot_create_refund(public_db: Path) -> None:
    conn = connect(public_db)
    try:
        borrowed = conn.execute(
            "SELECT approval_id FROM approvals WHERE claim_id <> 'C-001' LIMIT 1",
        ).fetchone()[0]
        conn.execute("UPDATE claims SET approval_id=? WHERE claim_id='C-001'", (borrowed,))
        conn.commit()
    finally:
        conn.close()
    result = orchestrator.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert result.error_reason == "approval_claim_mismatch"
    conn = connect(public_db)
    try:
        assert conn.execute(
            "SELECT COUNT(*) FROM audit_events WHERE claim_id='C-001' "
            "AND event_type='policy_denied'",
        ).fetchone()[0] == 1
    finally:
        conn.close()


def test_retries_have_exactly_one_commit_audit(public_db: Path) -> None:
    for seed in range(100, 106):
        result = orchestrator.run_claim("C-001", seed=seed, store_path=str(public_db))
        assert result.status == "resolved"
        assert result.committed_audit_count == 1
    assert_one_effect(public_db, "C-001")


@pytest.mark.parametrize("point", [
    "before_effect", "after_effect_before_checkpoint", "after_checkpoint",
])
def test_crash_fires_then_resume_commits_once(public_db: Path, point: str) -> None:
    with pytest.raises(InjectedCrash):
        orchestrator.run_claim("C-012", seed=11, store_path=str(public_db), crash_at=point)
    resumed = orchestrator.run_claim("C-012", seed=11, store_path=str(public_db))
    assert resumed.status == "resolved"
    assert_one_effect(public_db, "C-012")


def test_threaded_retries_keep_single_effect_and_audit(public_db: Path) -> None:
    def retry(seed: int) -> str:
        return orchestrator.run_claim("C-001", seed=seed, store_path=str(public_db)).status
    with ThreadPoolExecutor(max_workers=4) as executor:
        statuses = list(executor.map(retry, range(301, 309)))
    assert statuses == ["resolved"] * 8
    assert_one_effect(public_db, "C-001")
