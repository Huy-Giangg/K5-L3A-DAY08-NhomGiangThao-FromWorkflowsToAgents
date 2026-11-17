"""Kiểm can thiệp R2 chữa T02 và không thay implementation swarm gốc."""
from __future__ import annotations

from pathlib import Path

from bonus.swarm_no_ticket_override import run_claim
from lab8.shapes import swarm_reference


def test_r2_variant_denies_false_ticket_delay_and_restores_parser(public_db: Path) -> None:
    original = swarm_reference.parse_delay_days
    result = run_claim("C-002", seed=55, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.run_id == "R-swarm_no_ticket_override-C-002-s55"
    assert swarm_reference.parse_delay_days is original
