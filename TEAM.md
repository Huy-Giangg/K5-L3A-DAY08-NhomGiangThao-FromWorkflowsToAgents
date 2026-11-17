# Team

## Thông tin nhóm
- Tên nhóm: NhomGiangThao.
- Lớp: L3A.
- Repo nhóm: https://github.com/Huy-Giangg/K5-L3A-DAY08-NhomGiangThao-FromWorkflowsToAgents
- URL repo, nhánh nộp, commit chốt code: https://github.com/Huy-Giangg/K5-L3A-DAY08-NhomGiangThao-FromWorkflowsToAgents/tree/thao-orchestrator-evaluation; 97804c6c3948a5cd574b91a6ae5ddf486887bc76.
- Báo cáo được commit sau commit code theo SUBMISSION.md; mỗi thành viên tự nộp link LMS.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
| 1 | Lê Sông Thao | 2A202603534 | sirothao123@gmail.com | lesongthao | Thành viên B: Shape C, durability/security tests, benchmark, R2, ADR và tích hợp |
| 2 | Nguyễn Huy Giang | 2A202603543 | giangnh.vinuni@gmail.com | Huy-Giangg | Thành viên A: Shape A/B và test tương ứng |

## Bảng đóng góp

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Lê Sông Thao | Shape C, handoff, crash/retry, benchmark và nghiên cứu R2 | 97804c6c3948a5cd574b91a6ae5ddf486887bc76 | src/tests/test_member_b_handoff_security.py; src/tests/test_member_b_research.py |
| Nguyễn Huy Giang | Shape A workflow và Shape B single ReAct | 0d7c2997bca1583814cc2f2270a7b43c4d6ebc35 | src/tests/test_member_a_shapes.py |

## 2A202603534_LeSongThao
- Triển khai phần B, kiểm quote đầy đủ/approval/trace và một hiệu ứng tiền khi retry/crash.
- 13 ca kiểm bảo mật/độ bền và một test cho ablation.
- Benchmark 280 trial, nghiên cứu R2 140 trial, crash20/20 và safety scan.
- Báo cáo: report/team/2A202603534_LeSongThao.md.
- Trợ lý phát triển và cách kiểm chứng được khai báo trong báo cáo cá nhân.

## 2A202603543_NguyenHuyGiang
- Commit 0d7c299 có workflow.py, single.py và test_member_a_shapes.py.
- Đã tích hợp nguyên lịch sử nhánh origin/NguyenHuyGiang.
- Báo cáo cá nhân do Giang tự viết theo thống nhất; chưa có trong commit đã tích hợp.
