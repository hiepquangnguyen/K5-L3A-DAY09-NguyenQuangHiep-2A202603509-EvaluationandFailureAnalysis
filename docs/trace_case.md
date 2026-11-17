# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11` (trace run_id `R-seeded_regression-C-002-s11`; đối chứng cũng xuất hiện ở `swarm C-002@55`) |
| Triệu chứng | Grader Lab 8 `trial_pass` FAIL (`status resolved != denied`); event 6 `reply` nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."` và ledger ghi `refund_vnd=20000`, `refund_count=1`, trong khi nhãn chuẩn là `status=denied`, `refund_vnd=0`, `refund_count=0`. |
| Bước sai đầu tiên | Event **3** `model_override` — `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event 1 (`handoff`) giao đúng task `check_applicable_policy` và danh sách tool hợp lệ; Event 2 (`investigator`) gọi `lookup_order` truy vấn DB trả đúng đơn `O-202` (`status="delivered"`, `delay_days=2`). Tới Event 3 agent mới lấy số ngày tự khai `5` trong ticket ghi đè lên giá trị `2` của DB, dẫn tới Event 4 (`quote`) tính sai `20000` thay vì `0`. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Trên shape `fixed C-002@11`, sau Event 2 (`investigator`) **không có** event `model_override`; Event 3 đi thẳng sang `quote` với `{"amount_vnd": 0, "reason": "no_entitlement"}`, Event 4 `reply` từ chối đúng quy định và ledger ghi `refund_vnd=0` (`PASS`). |
| Regression test | `src/tests/test_lab9_trace_case.py` (`test_c002_seeded_regression_triggers_override_and_fails`, `test_c002_fixed_keeps_db_fact_and_passes`): dùng `DbFactKept` + kiểm tra `snapshot["refund_vnd"]` & `lab8_pass`; đã chạy xác nhận phát hiện fail trên `seeded_regression` và pass trên `fixed`. |
| Chưa chắc chắn | Trace hiện tại ghi nhận trạng thái sau khi `MockLLM` parse ticket, chưa phản ánh nguyên nhân ở tầng prompt/LLM thật khiến mô hình ưu tiên chữ trong ticket hơn kết quả tool DB (chỉ khẳng định được bước ghi đè dữ liệu xảy ra ở Event 3). |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
