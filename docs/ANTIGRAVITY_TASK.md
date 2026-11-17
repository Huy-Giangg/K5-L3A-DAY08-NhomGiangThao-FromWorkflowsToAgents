# Đề xuất mã Shape C — LAB08-MEMBER-B

Lượt trước bị sandbox chặn ghi workspace. Lượt này chỉ đề xuất mã qua phản hồi:
KHÔNG dùng tool, shell, đọc/ghi tệp, duyệt web hoặc kiểm quyền. Đủ mã nguồn/API được đính kèm.
Đây là review với đề xuất thay thế hoàn chỉnh; Codex sẽ áp dụng và kiểm thử.

Chỉ trả MỘT JSON object hợp lệ, không Markdown fence, không lời giải thích ngoài JSON:
{"files":{"src/lab8/shapes/orchestrator.py":"...toàn bộ mã...","src/tests/test_member_b_handoff_security.py":"...toàn bộ mã..."},"notes":"giới hạn/chưa chạy"}

Mỗi file <=300 dòng, type hints đủ. Không gọi model thật, không thay host, evaluator, data.
Giữ run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str|None=None)->RunResult.
Đọc get_claim_view, budget.add_tool(tool_cost()), trace chỉ claim_id/order_id/found.
Không tồn tại: failed/0; thiếu order_id: needs_info/0.
make_handoff(request_id=run_id, claim_id=claim_id, task="check_applicable_policy", facts={},
allowed_tools=["lookup_order","lookup_policy","compute_compensation"]).
trace.add("handoff", handoff đã lọc); run_readonly_investigators(conn,budget,handoff,principal_id).
order không visible → escalated/0. Quote từ kết quả runtime compute_compensation.
Quote <=0 → denied/0, không issue_refund. Quote>0 → issue_refund với quote đầy đủ, crash_at nguyên.
Không tự kiểm approval/trừ hoàn tiền trước; host ghi policy_denied. Conflict→failed, khác từ chối→denied, ok→resolved.
Mọi return dùng common.finish; kết nối đóng finally; InjectedCrash được propagate.
Có thể ghi trace crash rồi raise lại. Không ghi ticket/context/parent_secret/raw_headers/PII.
Không cần MockLLM. Không tự tạo exception tùy ý hoặc đọc nhãn expected.

Test dùng fixture public_db: Path từ tests/conftest.py; DB đã tạo đủ dữ liệu.
Claim C-001 hợp lệ quote35000; C-012 crash có cùng logic hoàn tiền; C-013 proposal35000 nhưng denied do đã hoàn đủ;
C-014 proposal150000, effect120000. C-002 delay2ngày denied; C-005 thiếuorder xem public fixture nếu không chắc thì tránh giả định.
API db.connect(path) row_factory sqlite3.Row. durability.get_refund(conn,cid), committed_audit_count(conn,cid).
Test spy actual make_handoff hoặc run_readonly_investigators để kiểm facts={} và đúng allowed_tools.
Lấy dữ liệu nhạy cảm bằng SELECT parent_secret,raw_headers_json từ claims và phone,address,item_name,internal_note từ orders
chỉ trong test để đối chiếu chúng KHÔNG xuất hiện ở handoff, trace, stdout.
Chạy lại nhiều lần phải một ledger và audit; khóa refund:C-001.
Test crash/resume parametrized: before_effect,after_effect_before_checkpoint,after_checkpoint.
Test ThreadPoolExecutor nhiều kết nối cùng C-001; dùng seed khác nhau cho trace riêng, kiểm effects/audit sau khi hoàn tất.
Không sửa test có sẵn; không giả vờ đã chạy kiểm thử. Ưu tiên 5–10 test có ý nghĩa.
