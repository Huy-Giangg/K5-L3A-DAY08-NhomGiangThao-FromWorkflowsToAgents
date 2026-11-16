"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)

    # 1. Read claim view through get_claim_view
    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    if not claim_view.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    trace.add("claim", {"claim_id": claim_view["claim_id"], "order_id": claim_view.get("order_id")})

    # 2. Define ReAct decide function
    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        claim = seen.get("claim") or {}
        # If missing order_id -> needs_info
        if not claim.get("order_id"):
            complete(budget, seed=seed, purpose="draft", prompt="needs_info")
            return {"final": {"status": "needs_info", "reason": "missing_order_id"}}

        last_tool = seen.get("last_tool")
        last_result = seen.get("last_result") or {}

        # Step 1: lookup order
        if last_tool is None:
            complete(budget, seed=seed, purpose="react", prompt=f"lookup_order {claim.get('order_id')}")
            return {
                "tool": "lookup_order",
                "args": {"order_id": claim.get("order_id"), "principal_id": claim.get("principal_id")},
            }

        # Step 2: check order visibility
        if last_tool == "lookup_order":
            if not last_result.get("visible"):
                complete(budget, seed=seed, purpose="draft", prompt="escalated")
                return {"final": {"status": "escalated", "reason": last_result.get("reason")}}
            # Order is visible, calculate quote through compute_compensation
            order = dict(last_result["order"])
            complete(budget, seed=seed, purpose="react", prompt=f"compute_compensation order={order['order_id']}")
            return {
                "tool": "compute_compensation",
                "args": {"order": order},
            }

        # Step 3: check compensation result
        if last_tool == "compute_compensation":
            quote = last_result
            proposal = int(quote.get("amount_vnd") or 0)
            complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
            if proposal <= 0:
                return {"final": {"status": "denied", "proposal": 0, "reason": quote.get("reason")}}
            return {"final": {"status": "resolved", "proposal": proposal, "reason": quote.get("reason")}}

        return {"final": {"status": "failed", "error_reason": "unknown_state"}}

    # 3. Run ReAct loop (max 8 steps)
    react_out = run_react(
        conn,
        budget,
        observation={"claim": claim_view},
        decide=decide,
        max_steps=8,
        worker=False,
    )

    final = react_out.get("final") or {}
    res_status = final.get("status")

    if res_status == "needs_info":
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("reason"),
        )

    if res_status == "escalated":
        trace.add("decision", {"status": "escalated"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("reason"),
        )

    if res_status == "denied":
        trace.add("decision", {"status": "denied", "reason": final.get("reason")})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("reason"),
        )

    if res_status == "failed":
        trace.add("error", {"reason": final.get("error_reason") or "failed"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("error_reason"),
        )

    # If resolved, proposal > 0: call host issue_refund with full quote
    proposal = int(final.get("proposal") or 0)
    trace.add("decision", {"status": "resolved", "proposal": proposal})

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )

    return finish(
        conn,
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
