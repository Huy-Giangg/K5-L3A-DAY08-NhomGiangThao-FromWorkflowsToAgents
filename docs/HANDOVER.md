# Bàn giao LAB08-MEMBER-B

- Trạng thái: IN_PROGRESS.
- Người giao/review: Codex. Người triển khai Shape C/test: Antigravity CLI.
- Chủ sở hữu phần B: Lê Sông Thao, 2A202603534.
- Git base đã tích hợp: 0d7c299 (Giang: workflow, single, test_member_a_shapes.py).
- Working tree có TEAM.md sửa từ trước và scripts/ công cụ địa phương; giữ nguyên.
- Không commit, push, merge, cài package, sửa cấu hình hoặc mở rộng quyền trong lượt Antigravity.

## Mục tiêu và quyền sửa của Antigravity

Chỉ sửa/tạo hai tệp:
1. src/lab8/shapes/orchestrator.py.
2. src/tests/test_member_b_handoff_security.py.

Codex phụ trách PRD, ARCHITECTURE, nghiên cứu/ablation, benchmark, reports và TEAM.
Mỗi thời điểm một người sửa cùng tệp. Người nhận tự kiểm yêu cầu với artifact gốc.
Đọc CHECKPOINTS.md, docs/business_rules.md, docs/contracts.md, lab8/handoff.py,
runtime.py, shapes/common.py, schemas.py, db.py, tools.py, durability.py và test có sẵn.
Không sửa host, grader, metrics, policy, config, data, test có sẵn hoặc A/B của Giang.

## Hợp đồng Shape C

Giữ run_claim(claim_id: str, *, seed: int, store_path: str,
crash_at: str | None = None) -> RunResult.
Mỗi hàm đầy đủ type hints; mỗi tệp không quá 300 dòng.

- Mở kết nối rồi luôn đóng trong finally.
- Đọc get_claim_view; không SELECT nguyên claim để đưa vào handoff/trace.
- Claim không tồn tại → failed/proposal 0; thiếu order_id → needs_info/0.
- Dùng make_handoff với facts={} hoặc chỉ FACT_KEYS lấy từ nguồn an toàn.
- allowed_tools đúng thứ tự: lookup_order, lookup_policy, compute_compensation.
- Chạy run_readonly_investigators với principal_id từ claim đã đọc.
- Trace chỉ chứa handoff đã sanitize; không parent context, ticket, secret, raw headers hoặc order thô.
- Order không visible → escalated/0.
- Tiền tính bằng compute_compensation qua runtime/code; không dùng MockLLM quyết tiền.
- Truyền QUOTE ĐẦY ĐỦ dạng int vào durability.issue_refund(..., crash_at=crash_at);
  host tự trừ hoàn tiền trước và kiểm approval. Không tự cap/trừ trước.
- Quote 0 → denied/0, không gọi host. Quote dương phải gọi host kể cả khi approval thiếu;
  host từ chối → denied, proposal giữ quote và có audit policy_denied.
- Conflict → failed; thành công → resolved. Trả mọi nhánh bằng common.finish.
- make_run_id("orchestrator", claim_id, seed); Budget đúng các tool calls thực tế.
- Không gọi model nếu không cần. Không nuốt InjectedCrash; nếu ghi trace khi crash phải raise lại.
- Khóa refund:{claim_id} và transaction do host quản lý, không tự ghi ledger.

## Test mới bắt buộc (hành vi, không chỉ đọc chuỗi code)

- Quan sát handoff thực tế truyền đến investigator: không canary/parent_secret/headers/PII;
  facts và allowed_tools đúng allowlist. Trace/stdout không lộ dữ liệu bị cấm.
- Retry nhiều lần cùng claim → một ledger, một audit refund_committed.
- Crash/resume qua các điểm được host hỗ trợ → không double refund, crash thực sự được ném.
- Ít nhất một bài retry bằng nhiều kết nối/thread; kiểm ledger và audit sau khi các thread hoàn tất.
  Không yêu cầu đọc trace cùng run_id trong khi các thread đang ghi.
- Các trường hợp approval và T13/T14 vẫn giữ proposal đầy đủ.

## Kiểm tra

Chạy trong src/. Nếu có .venv/Scripts/python.exe, dùng executable đó thay cho python.
- python -m pytest -q tests/test_member_b_handoff_security.py
- python -m pytest -q -m student -o addopts= -k orchestrator (62 passed)
- python -m pytest -q

## Kết quả bàn giao

Chỉ ghi phản hồi trong CLI: tệp sửa, số dòng, lệnh đã chạy, mã thoát, pass/fail, lỗi còn lại.
Không sửa tệp bàn giao này vì Codex đang quản lý. Khi xong, báo READY_FOR_REVIEW.
Chưa có kết quả nghiệm thu tại thời điểm giao; không chép kỳ vọng thành kết quả thật.
