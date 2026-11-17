# Báo cáo cá nhân — Lê Sông Thao

## 1. Thông tin thành viên
- Họ tên: Lê Sông Thao.
- MSSV: 2A202603534.
- Email: sirothao123@gmail.com; VinUni: 26ai.thaols@vinuni.edu.vn.
- GitHub: lesongthao.

## 2. Phần việc phụ trách
Shape C, handoff chỉ đọc, retry/crash, thực nghiệm bốn shape, nghiên cứu R2 và tổng hợp ADR/báo cáo.
Giang phụ trách A/B; lịch sử commit của Giang được giữ khi tích hợp.

## 3. Đóng góp cụ thể
- Commit kỹ thuật: 97804c6c3948a5cd574b91a6ae5ddf486887bc76.
- Orchestrator dùng make_handoff với facts={} và ba tool chỉ đọc; tiền tính qua code và host ghi refund.
- Truyền quote đầy đủ, crash_at; đóng kết nối; giữ proposal khi host cap/từ chối.
- Test mới: test_member_b_handoff_security.py (13 ca) và test_member_b_research.py (1 ca).
- R2 tách wrapper để không sửa swarm tham chiếu, dùng cùng corpus/seed/evaluator.
- Chạy benchmark/crash/safety audit và lập báo cáo bằng số liệu JSON chương trình sinh.

## 4. Bằng chứng
- Commit: https://github.com/Huy-Giangg/K5-L3A-DAY08-NhomGiangThao-FromWorkflowsToAgents/commit/97804c6c3948a5cd574b91a6ae5ddf486887bc76.
- Cổng host: 76 passed; ma trận student: 248 passed; crash 20/20.
- Shape C: 70/70 public trial, cost/success 46.428571 VND mô phỏng.
- Benchmark: src/reports/benchmark.json; ví dụ run R-orchestrator-C-014-s11.
- R2: src/reports/research_r2_ablation.json; C-002/seed55 được sửa ở variant.
- Safety: src/reports/member_b_safety.json, 0 dấu rò/approval bypass theo phạm vi public.

## 5. Công cụ AI đã dùng
Codex tích hợp, review, bổ sung test, thực nghiệm và tổng hợp tài liệu.
Antigravity CLI đề xuất mã Shape C và test qua phản hồi sau khi sandbox chặn ghi trực tiếp.
Đề xuất AI chưa được coi là nghiệm thu: Codex đã sửa API refund/fixture sai, chạy test và đối chiếu ledger/trace.
Code Lab dùng MockLLM theo đề bài; việc dùng CLI thật chỉ phục vụ phát triển.
Số liệu, run id và hash lấy từ chương trình/Git, không tự tạo cho báo cáo.

## 6. Tự đánh giá kỹ thuật
Phần đã có bằng chứng: handoff allowlist, một refund/audit khi retry/crash, approval bị mượn bị từ chối,
T13 giữ proposal35000 nhưng không refund mới, T14 proposal150000 và effect120000.
Nội dung cần tự trình bày khi bảo vệ: vì sao host nhận quote đầy đủ, vì sao checkpoint chưa đủ chống trả trùng,
và vì sao chọn workflow dù phần triển khai cá nhân là Shape C.
Chưa có số liệu hidden, phần cứng hay model sản xuất; không suy rộng kết quả public thành bảo đảm tổng quát.
