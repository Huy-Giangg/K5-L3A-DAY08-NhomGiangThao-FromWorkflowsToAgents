# Decision record

- Shape chọn: workflow
- Commit hash: 97804c6c3948a5cd574b91a6ae5ddf486887bc76
- Run id dẫn chứng: R-workflow-C-001-s11; src/reports/benchmark.json (280 trial, 14 claim × 5 seed × 4 shape)
- Pass rate / pass^5 / seed min-max / variance: 1.000000 / 1.000000 / 1.000000–1.000000 / 0.00000000
- Cost per success (mô phỏng, VND): 28.790000
- Crash safety: 20/20 (src/reports/crash.json); T11/T12 và test_member_b_handoff_security.py kiểm trực tiếp retry/crash của Shape C
- Secret leak / approval bypass: 0 / 0 trên public theo src/reports/member_b_safety.json; không có kết quả hidden

## Vì sao shape này
Workflow đạt 70/70 trial, pass^5=1, variance=0 và chi phí thấp nhất trong bốn triển khai đang so.
Claims flow chủ yếu tuần tự: đọc claim → đọc order → tính quote bằng code → host kiểm quyền và ghi ledger.
Vì vậy chọn kiến trúc ít tự chủ nhất đã làm được việc. Shape C cũng đạt 70/70 nhưng chi phí
46.428571 VND/success do thêm lượt đọc/handoff; chưa tạo lợi ích pass trên corpus này.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success VND | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.00000000 | 28.790000 | 3.071429/4 |
| single | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.00000000 | 29.572857 | 2.000000/2 |
| orchestrator | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.00000000 | 46.428571 | 2.785714/3 |
| swarm | 0.985714 | 0.928571 | 0.928571–1.000000 | 0.00081633 | 49.566957 | 2.800000/3 |

## Có đáng đổi lấy multi-agent không
Chưa có bằng chứng đáng đổi trong public benchmark. Cần xem lại nếu có các nhánh điều tra độc lập,
nguồn dữ liệu khác quyền sở hữu hoặc nhu cầu triển khai worker riêng. Phải đo lại trên cùng dữ liệu và seed.
Số model calls/tool calls và cách ghi trace khác nhau giữa implementation; không quy toàn bộ chênh lệch chi phí
cho topology. Đặc biệt Shape C không gọi MockLLM, còn A có một lượt soạn câu trả lời; tool call vẫn có giá mô phỏng.

## Trace và bằng chứng
Shape C ghi claim_view đã chọn trường, handoff đã sanitize, quote và crash nếu có.
Không ghi ticket, parent_secret, raw headers, phone, address, item_name hoặc internal_note.
13 ca test mới kiểm handoff thực, early returns, approval, T13/T14, retry, crash/resume và nhiều thread.
Quét lại 280 trace public không phát hiện canary/PII theo bộ dấu cấm; kiểm ledger nằm trong evaluator và test.
Crash suite 20/20 chủ yếu kiểm host/swarm, nên không dùng riêng nó để khẳng định Shape C an toàn.

## Giới hạn
MockLLM không phải model sản xuất; latency unavailable; giá là mô phỏng, không phải hóa đơn API.
Chưa có student_drop hoặc kết quả hidden của giảng viên. Commit trên là commit kỹ thuật được benchmark;
báo cáo được commit sau theo quy trình SUBMISSION.md.
