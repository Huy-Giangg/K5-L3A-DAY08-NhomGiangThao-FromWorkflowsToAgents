"""Module Shape C: Orchestrator điều phối xử lý khiếu nại (Claim Processing).

Tuân thủ nguyên tắc Least Privilege: Handoff dữ liệu đã được làm sạch sang
Investigator chỉ đọc, kiểm soát hoàn tiền bền vững qua tầng host durability.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes import common
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE_NAME = "orchestrator"


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    """Điều phối toàn bộ vòng đời khiếu nại của Shape C.

    Args:
        claim_id: Mã định danh khiếu nại.
        seed: Seed sinh số ngẫu nhiên phục vụ tái hiện log/trace.
        store_path: Đường dẫn tới tệp cơ sở dữ liệu SQLite.
        crash_at: Điểm tiêm lỗi mô phỏng sự cố (crash injection).

    Returns:
        RunResult: Kết quả thực thi chuẩn hóa của phiên xử lý.
    """
    run_id = make_run_id(SHAPE_NAME, claim_id, seed)
    trace = Trace(run_id)
    budget = Budget()
    conn = connect(store_path)

    try:
        # Bước 1: Tra cứu thông tin khiếu nại (Claim View)
        claim_raw = get_claim_view(conn, claim_id)
        budget.add_tool(tool_cost())

        is_found = bool(claim_raw.get("found", False))
        order_id = claim_raw.get("order_id")
        principal_id = claim_raw.get("principal_id", "")

        # Ghi nhận vết an toàn (không ghi PII hay secret)
        trace.add(
            "claim_view",
            {
                "claim_id": claim_id,
                "found": is_found,
                "order_id": order_id,
            },
        )

        # Kiểm tra tồn tại
        if not is_found:
            return common.finish(
                conn,
                shape=SHAPE_NAME,
                claim_id=claim_id,
                seed=seed,
                status="failed",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="claim_not_found",
            )

        # Kiểm tra thiếu mã đơn hàng
        if not order_id:
            return common.finish(
                conn,
                shape=SHAPE_NAME,
                claim_id=claim_id,
                seed=seed,
                status="needs_info",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="missing_order_id",
            )

        # Bước 2: Thiết lập hợp đồng chuyển giao (Handoff) cho điều tra viên
        handoff = make_handoff(
            request_id=run_id,
            claim_id=claim_id,
            task="check_applicable_policy",
            facts={},  # Chủ động rỗng để ngăn chặn rò rỉ dữ liệu ngoài ý muốn
            allowed_tools=[
                "lookup_order",
                "lookup_policy",
                "compute_compensation",
            ],
        )
        trace.add("handoff", handoff)

        # Bước 3: Chạy điều tra viên ở chế độ chỉ đọc
        investigation = run_readonly_investigators(
            conn,
            budget,
            handoff,
            principal_id=principal_id,
        )

        tools_res: dict[str, Any] = investigation.get("tools", {})
        order_res: dict[str, Any] = tools_res.get("lookup_order", {})

        # Đơn hàng không hiển thị hoặc vượt phạm vi phân quyền
        if not order_res.get("visible", False):
            return common.finish(
                conn,
                shape=SHAPE_NAME,
                claim_id=claim_id,
                seed=seed,
                status="escalated",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=order_res.get("reason", "order_not_visible"),
            )

        # Bước 4: Đánh giá báo giá bồi thường (Compensation Quote)
        comp_res: dict[str, Any] = tools_res.get("compute_compensation", {})
        quote_amount = int(comp_res.get("amount_vnd", 0))
        trace.add("quote", comp_res)

        if quote_amount <= 0:
            return common.finish(
                conn,
                shape=SHAPE_NAME,
                claim_id=claim_id,
                seed=seed,
                status="denied",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason=comp_res.get("reason", "policy_denied"),
            )

        # Bước 5: Thực hiện hoàn tiền bền vững qua Host Durability
        refund_outcome = issue_refund(
            conn,
            claim_id,
            quote_amount,
            crash_at=crash_at,
        )

        if refund_outcome["conflict"]:
            final_status = "failed"
            error_reason = refund_outcome.get("reason", "refund_conflict")
        elif refund_outcome["ok"]:
            final_status = "resolved"
            error_reason = None
        else:
            final_status = "denied"
            error_reason = refund_outcome.get("reason", "policy_denied")

        return common.finish(
            conn,
            shape=SHAPE_NAME,
            claim_id=claim_id,
            seed=seed,
            status=final_status,
            proposal_amount=quote_amount,
            budget=budget,
            trace=trace,
            error_reason=error_reason,
        )

    except InjectedCrash:
        trace.add("crash", {"crash_at": crash_at})
        trace.write()
        raise
    finally:
        conn.close()
