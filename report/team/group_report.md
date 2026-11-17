# Báo cáo nhóm — Lab08 LogiX-VN

## 1. Thông tin nhóm
- Nhóm: NhomGiangThao; lớp L3A.
- Nguyễn Huy Giang: 2A202603543; Lê Sông Thao: 2A202603534.
- Repo: https://github.com/Huy-Giangg/K5-L3A-DAY08-NhomGiangThao-FromWorkflowsToAgents
- Commit chốt code (trùng ADR): 97804c6c3948a5cd574b91a6ae5ddf486887bc76; nhánh tích hợp: feat/cp1-team-thao.
- Giang tự hoàn thiện báo cáo cá nhân; báo cáo này không viết thay phần tự đánh giá của Giang.

## 2. Mục tiêu và cách tiếp cận
So sánh bốn kiến trúc trên cùng claims flow, chọn mức tự chủ thấp nhất đủ xử lý.
Giang triển khai A/B trong commit 0d7c299; tích hợp fast-forward để giữ lịch sử.
Thao phụ trách C, bảo mật handoff, độ bền, benchmark, nghiên cứu R2 và tổng hợp bằng chứng.
Mọi phép tính tiền và quyền ghi do code/host quản lý; ticket là dữ liệu không đáng tin.

## 3. Giải pháp
- A: workflow cố định đọc claim/order, compute_compensation, draft và host refund.
- B: vòng ReAct giới hạn 8 bước với công cụ đọc; chỉ code ngoài vòng lặp gọi host.
- C: make_handoff với facts rỗng, chỉ ba tool lookup_order/lookup_policy/compute_compensation;
  run_readonly_investigators trả order view và quote. Orchestrator gửi quote đầy đủ vào host.
- D: swarm tham chiếu của đề bài, giữ nguyên điểm yếu seed55 làm đối chứng.
Host kiểm approval đúng claim, trần theo order, idempotency refund:claim_id và transaction tiền/audit.
C ghi trace đã lọc; không chuyển parent context hay PII sang investigator. Kết nối luôn đóng trong finally.
Đọc thêm docs/architecture.md và docs/contracts.md.

## 4. Kết quả và đánh giá
Nguồn: src/reports/benchmark.json, 4 shape × 14 claim × 5 seed = 280 trial; SQLite mới cho mỗi trial.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success VND | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.00000000 | 28.790000 | 3.071429/4 |
| single | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.00000000 | 29.572857 | 2.000000/2 |
| orchestrator | 1.000000 | 1.000000 | 1.000000–1.000000 | 0.00000000 | 46.428571 | 2.785714/3 |
| swarm | 0.985714 | 0.928571 | 0.928571–1.000000 | 0.00081633 | 49.566957 | 2.800000/3 |

Cả A/B/C đều đạt 70/70 public trial. Swarm đạt 69/70, lỗi duy nhất C-002/seed55.
Cổng kiểm thử: 76 passed (host + test nhóm), 248 passed (student); tổng 324 ca.
Test riêng Thao: 13 ca handoff/approval/retry/crash/concurrency và 1 ca ablation.
Crash safety: 20/20; ba điểm crash được kiểm trực tiếp với Shape C.
Quét 280 trace theo bộ dấu cấm không phát hiện secret/PII; không có status resolved trên nhãn approval không hợp lệ.
Cổng ledger/effect được evaluator đối chiếu, không chỉ dựa vào status tự khai.

Chọn workflow: cùng độ đúng với B/C, chi phí thấp nhất và điều khiển dễ giải thích.
Mean/p95 steps là số event trace, không phải thời gian hoặc số suy luận; không suy ra latency từ bảng.
Chi tiết tại decision_adr.md.

Nghiên cứu R2 giữ cùng biến kiểm soát, chỉ tắt nguồn delay từ ticket trong wrapper:
swarm 69/70→70/70, pass^5 13/14→14/14, variance 0.00081633→0;
cost/success 49.566957→48.715714.
Đây là lỗi kiểm chứng căn cứ theo cách diễn giải MAST của nhóm; xem research_card.md.

## 5. Khó khăn và cách xử lý
- TEAM ban đầu ghi ngược vai trò; sửa theo commit và phân công thực tế.
- Pytest toàn máy là 9.2, ngoài khoảng đề bài: dùng src/.venv với pytest8.4.2 và PyYAML6.0.3.
- Sandbox Windows chặn cache/tmp cũ: tạo src/.pytest_tmp, dùng --basetemp và -p no:cacheprovider.
  Không sửa test/host để bỏ kiểm tra.
- Antigravity bị chặn ghi: chuyển sang đề xuất code qua phản hồi, Codex review và áp dụng.
  Review phát hiện lời gọi refund sai API và fixture sai; đã sửa trước khi test.
- Không sửa JSON report bằng tay hoặc các tệp thước đo.

## 6. Tổng hợp đóng góp
Giang: workflow.py, single.py, test_member_a_shapes.py, commit 0d7c299.
Thao: orchestrator.py, test_member_b_handoff_security.py, test_member_b_research.py,
thực nghiệm/safety audit và báo cáo; commit kỹ thuật 97804c6.
Bảng chi tiết trong TEAM.md; báo cáo Thao: 2A202603534_LeSongThao.md.

## 7. Hạn chế và hướng cải thiện
MockLLM không phải model thật, latency unavailable và chi phí mô phỏng.
Chưa có hidden/student_drop; public pass không chứng minh đạt ngưỡng hidden.
Số lượt tool/model và thiết kế trace khác giữa implementation là yếu tố cần tính khi diễn giải cost/steps.
Chỉ cân nhắc tăng mức tự chủ khi có nhu cầu điều tra độc lập và số liệu mới chứng minh lợi ích.

## 8. Tài liệu tham khảo
- Đề bài: CHECKPOINTS.md, docs/business_rules.md, docs/contracts.md, docs/metrics.md, RULES.md.
- MAST: Cemri và cộng sự, 2025, https://arxiv.org/abs/2503.13657v3.
- Code A/B của Giang: https://github.com/Huy-Giangg/K5-L3A-DAY08-NhomGiangThao-FromWorkflowsToAgents/commit/0d7c2997bca1583814cc2f2270a7b43c4d6ebc35.
- Công cụ phát triển: Codex để tích hợp/review/thực nghiệm; Antigravity CLI đề xuất Shape C/test.
  Runtime bài Lab chỉ gọi MockLLM, không gọi model/API thật.
