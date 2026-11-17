# Báo cáo cá nhân — Nguyễn Huy Giang

## 1. Thông tin thành viên
- Họ tên: Nguyễn Huy Giang.
- MSSV: 2A202603543.
- Email: giangnh.vinuni@gmail.com; VinUni: 26ai.giangnh@vinuni.edu.vn.
- GitHub: Huy-Giangg.

## 2. Phần việc phụ trách
- Triển khai Shape A (Deterministic Workflow) và Shape B (Single ReAct Agent).
- Ranh giới Code vs Model: Đảm bảo số tiền bồi thường tính bằng code (`compute_compensation`), MockLLM chỉ đóng vai trò draft nội dung.
- Xây dựng bộ kiểm thử cá nhân cho Shape A & Shape B (`src/tests/test_member_a_shapes.py`).
- Tuân thủ Trace Contract v1, đảm bảo không rò rỉ bí mật `CANARY_SECRET_*` hay PII.

## 3. Đóng góp cụ thể
- Commit kỹ thuật: 0d7c2997bca1583814cc2f2270a7b43c4d6ebc35 (`feat(shapes): implement Shape A (Workflow) & Shape B (Single ReAct) with tests by Nguyen Huy Giang`).
- Triển khai Shape A (`src/lab8/shapes/workflow.py`):
  + Đọc claim an toàn qua `get_claim_view`, bắt điều kiện thiếu mã đơn (`needs_info`, proposal 0).
  + Kiểm tra quyền sở hữu đơn hàng với `lookup_order`, rẽ nhánh `escalated` khi ngoài phạm vi hoặc không tìm thấy, không làm lộ SĐT, địa chỉ, tên hàng hay ghi chú nội bộ.
  + Tính quote chuẩn từ order row, bỏ qua câu chữ trong ticket; quote <= 0 trả về `denied`.
  + Quote > 0 gọi `durability.issue_refund` với quote đầy đủ, chuyển tiếp `crash_at` và không bắt `InjectedCrash`.
- Triển khai Shape B (`src/lab8/shapes/single.py`):
  + Thiết lập vòng lặp ReAct `lab8.runtime.run_react` với chặn cứng `max_steps=8`.
  + Ràng buộc ranh giới: ReAct agent chỉ được gọi tool đọc (`lookup_order`, `compute_compensation`), tuyệt đối không cấp quyền ghi `issue_refund` trong vòng lặp.
  + Phản ứng kháng prompt injection: Tính quote dựa trên DB thật, ngăn chặn việc khách hàng bịa đặt số ngày trễ trong ticket.
  + Sau vòng lặp, host bên ngoài thực thi `durability.issue_refund` với quote đầy đủ và chuyển tiếp `crash_at`.
- Xây dựng 8 unit test cases mới (`src/tests/test_member_a_shapes.py`):
  + Phòng thủ prompt injection (claim C-009).
  + Xử lý thiếu `order_id` (claim C-004) không ghi ledger.
  + Tuân thủ Trace Contract v1 và kiểm tra không rò rỉ bí mật/PII.
  + Kiểm tra sự lan truyền tự nhiên của `InjectedCrash`.

## 4. Bằng chứng
- Commit kỹ thuật: https://github.com/Huy-Giangg/K5-L3A-DAY08-NhomGiangThao-FromWorkflowsToAgents/commit/0d7c2997bca1583814cc2f2270a7b43c4d6ebc35.
- Cổng host: 76/76 passed (`python -m pytest -q`).
- Ma trận student: Shape A và Shape B đạt 62/62 passed trên từng shape (tổng cộng 124 passed).
- Test cá nhân: 8/8 passed (`python -m pytest -q tests/test_member_a_shapes.py`).
- Benchmark công cộng: Cả Shape A và Shape B đạt pass rate 1.000000 (70/70 trial), pass^5 1.000000, variance 0.00000000 (`src/reports/benchmark.json`).
- Crash safety: 20/20 (`src/reports/crash.json`), vượt qua kiểm tra T11, T12.

## 5. Công cụ AI đã dùng
- Trợ lý AI (Antigravity / Gemini) được sử dụng để hỗ trợ rà soát các nhánh điều kiện biên (edge cases), kiểm tra tuân thủ chữ ký hàm và cấu trúc trace JSON theo đúng hợp đồng đề bài.
- Tự kiểm tra và thẩm định: Mọi đoạn mã đều được chạy thử nghiệm thực tế với pytest, ma trận student T01–T14 trên cả 5 seeds, đối chiếu số liệu SQLite ledger thật để đảm bảo không vi phạm các tiêu chí must-pass.

## 6. Tự đánh giá
- Hoàn thành đầy đủ 100% nhiệm vụ được phân công theo Checkpoints CP1–CP5.
- Code đáp ứng nghiêm ngặt 3 tiêu chí must-pass: không bao giờ refund khi thiếu approval, không lộ chuỗi canary trong trace/output, và crash safety đảm bảo idempotency.
- Phối hợp nhịp nhàng với Thành viên B (Lê Sông Thao): Tích hợp sạch 100% không xung đột code, thống nhất chọn Shape A (Workflow) trong ADR vì chi phí thấp nhất (28.79 VND/success) mà vẫn đạt pass rate tuyệt đối 100%.
