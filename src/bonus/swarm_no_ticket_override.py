"""Ablation R2: giữ swarm, chỉ vô hiệu hóa nguồn delay từ ticket.

Chạy tuần tự trong nghiên cứu; mock.patch không dành cho benchmark đa luồng.
Đổi định danh trace để hai nhánh thí nghiệm không ghi đè bằng chứng của nhau.
"""
from __future__ import annotations

from unittest.mock import patch

from lab8.schemas import RunResult, make_run_id
from lab8.shapes import swarm_reference

VARIANT = "swarm_no_ticket_override"


def _variant_run_id(shape: str, claim_id: str, seed: int) -> str:
    del shape
    return make_run_id(VARIANT, claim_id, seed)


def run_claim(
    claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None,
) -> RunResult:
    with (
        patch.object(swarm_reference, "parse_delay_days", return_value=None),
        patch.object(swarm_reference, "make_run_id", side_effect=_variant_run_id),
    ):
        result = swarm_reference.run_claim(
            claim_id, seed=seed, store_path=store_path, crash_at=crash_at,
        )
    result.shape = VARIANT
    return result
