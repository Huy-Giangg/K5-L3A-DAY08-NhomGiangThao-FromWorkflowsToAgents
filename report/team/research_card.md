# Research card

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R2 — Failure taxonomy |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Cemri và cộng sự, NeurIPS 2025, nghiên cứu thực nghiệm: https://arxiv.org/abs/2503.13657v3 ; https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html |
| CLAIM | Một kết luận gốc của nguồn | MAST phân 14 dạng lỗi thành ba nhóm: thiết kế hệ thống, lệch phối hợp giữa agent và kiểm chứng tác vụ. |
| BOUNDARY | Model / dataset / setup | Paper nghiên cứu MAST-Data với hơn 1.600 trace từ 7 framework; không trực tiếp đánh giá LogiX/MockLLM. Phân loại lỗi Lab là diễn giải của nhóm. |
| HYPOTHESIS | Nếu đổi một thành phần, metric thay đổi | Tắt việc dùng delay parse từ ticket sẽ sửa C-002/seed55: pass 69/70→70/70, variance→0; cost/success không tăng. |
| METHOD | Biến cố định / biến thay đổi | Giữ world, 14 claim, MockLLM, seed 11/22/33/44/55, tool registry, giá, host và evaluator. Chỉ đổi parse_delay_days thành None trong wrapper; không tắt sanitization hay sửa swarm gốc. Run id tách nhánh để tránh ghi đè trace. |
| FAILURE / METRIC | Lỗi và phép đo | task_verification: không đối chiếu delay từ ticket với order có cấu trúc. Đo pass rate, pass^5, variance và simulated cost/success; failure_analysis lưu cặp run id. |

## Kết quả ablation
- Lệnh đã chạy trong src/: python -m bonus.member_b_research --out reports/research_r2_ablation.json
- Kiểm hồi quy: python -m pytest -q tests/test_member_b_research.py
- File report: src/reports/research_r2_ablation.json.
- Run baseline: R-swarm-C-002-s55; variant: R-swarm_no_ticket_override-C-002-s55.
- Commit code: 97804c6c3948a5cd574b91a6ae5ddf486887bc76; provenance trong report ghi HEAD và SHA-256 nguồn swarm tham chiếu.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success VND | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| swarm | 0.985714 | 0.928571 | 0.928571–1.000000 | 0.00081633 | 49.566957 | 2.800000/3 |
| swarm_no_ticket_override | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.00000000 | 48.715714 | 2.785714/3 |

Hypothesis được ủng hộ trên corpus này. Baseline có đúng một trial fail: C-002/seed55, status resolved thay vì denied.
Ticket nói trễ 5 ngày trong khi order là 2 ngày; host vẫn chấp nhận vì approval hợp lệ cho số tiền đề xuất.
Vì vậy đây là lỗi căn cứ/kiểm chứng nghiệp vụ, không phải bypass approval hoặc lỗi handoff.
Variant sửa trial đó; không có bằng chứng để kết luận mọi swarm/model thật đều có cùng lỗi.

## Giới hạn
MockLLM, 14 public claim, một can thiệp nhỏ; latency unavailable.
Wrapper dùng patch trong tiến trình tuần tự, không dành cho chạy nhiều thread.
Không lấy thí nghiệm tắt sanitization vì việc đó không cần thiết để kiểm giả thuyết và có thể gây rò dữ liệu.
Đây là research card bắt buộc, không tự nhận điểm bonus hoặc đăng ký topic.
