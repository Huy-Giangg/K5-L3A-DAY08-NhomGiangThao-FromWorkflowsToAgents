# Lab08 — phạm vi tích hợp thành viên B

## Người dùng và mục tiêu
Nhóm Giang–Thao hoàn thành claims LogiX-VN trên cùng contract, dữ liệu và evaluator.
Giang đã commit Shape A/B tại 0d7c299; Thao phụ trách Shape C, độ bền, thực nghiệm và báo cáo.

## Đầu vào/đầu ra
- run_claim: claim_id, seed, SQLite store_path, crash_at → RunResult + trace mới.
- Investigator: handoff allowlist + principal_scope → order view/policy/quote chỉ đọc.
- Host: claim_id + quote đầy đủ + crash_at → chấp nhận/từ chối/conflict; hiệu ứng ledger.
- Thực nghiệm: 14 public claim × 5 seed × 4 shape → benchmark.json.
- Crash suite chuẩn → crash.json; nghiên cứu R2 → báo cáo ablation riêng.

## Nghiệm thu
1. Orchestrator 62 ca student đạt; cổng host giữ xanh; test mới kiểm handoff, PII và retry/crash.
2. Crash chuẩn 20/20; bổ sung bằng chứng crash/retry trực tiếp của orchestrator.
3. Báo cáo do chương trình sinh; không sửa JSON bằng tay hoặc sửa thước đo.
4. ADR chọn shape theo số liệu, ghi code commit và run id thật.
5. Research card giữ biến cố định và thay một cơ chế, ghi kết luận đúng giới hạn.
6. TEAM và báo cáo cá nhân ghi đóng góp thực tế, khai báo trợ lý AI và phần chưa kiểm chứng.

Không tự nhận có kết quả hidden khi chưa có student_drop/nhãn chấm của giảng viên.
