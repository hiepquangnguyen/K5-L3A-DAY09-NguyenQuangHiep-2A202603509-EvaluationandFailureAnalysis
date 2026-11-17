# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có (PASS) | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không (FAIL — κ và R quá thấp) | loại |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / Hành động sửa rubric |
|---|---|---|---|---|---|
| 1 | `H-008` (`tone`) | PASS | FAIL | Người đúng | Xưng `"em"` + `"nha"` quá suồng sã; sửa rubric cấm xưng hô thân mật quá mức dù giọng thân thiện. |
| 2 | `H-029` (`tone`) | PASS | FAIL | Người đúng | Có cụm ra lệnh `"không cần nhắn thêm"`, judge bị đánh lừa bởi `"Dạ, vui lòng"`; bổ sung negative example giọng ra lệnh vào rubric. |
| 3 | `H-042` (`tone`) | FAIL | PASS | Người đúng | Câu ngắn nhưng lịch sự và đủ ý; bỏ điều kiện bắt buộc phải có câu xin lỗi ở mọi câu trả lời thành công. |
| 4 | `H-051` (`tone`) | FAIL | PASS | Người đúng | Dùng từ `"refund"` được CSKH LogiX cho phép; cập nhật danh sách thuật ngữ hợp lệ trong rubric. |
| 5 | `H-063` (`tone`) | PASS | FAIL | Người đúng | Hứa `"sẽ hoàn thêm"` ngoài kết quả hệ thống; thêm quy tắc cấm cam kết khoản hoàn bổ sung không có căn cứ. |
| 6 | `H-081` (`tone`) | FAIL | PASS | Judge đúng | Nhãn người đánh nhầm khi đọc ticket (`judge` phát hiện đúng); sửa nhãn vàng cho `H-081` trước lần audit sau. |
| 7 | `HL-015` (`helpful`) | PASS | FAIL | Người đúng | Reply báo `55.000đ` nhưng ledger chỉ ghi `40.000đ`; judge không thấy ledger nên không thể chấm tính đúng đắn tiền tệ (chuyển sang code grader FM-08). |
| 8 | `HL-016` (`helpful`) | PASS | FAIL | Người đúng | Câu xin lỗi dài dòng nhưng sai số tiền (`55.000đ` vs ledger `35.000đ`); judge mắc thiên kiến câu dài (verbosity bias) → **FN rất cao**. |

## Kết luận
- **Tiêu chí bị loại (`helpful`) và lý do:** Ma trận nhầm lẫn cho thấy `{'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70}` (`Recall = 0.300`, `κ = 0.375`). Trong 30 ca thực tế bị lỗi, judge bỏ sót tới **21 ca (`FN = 21`)**, khiến tỉ lệ lỗi quan sát chỉ là `0.09` dù tỉ lệ lỗi thực tế sau hiệu chỉnh Rogan–Gladen là `0.30`. Nguyên nhân gốc là judge chấm dựa trên bề mặt câu chữ lịch sự/dài dòng mà không có dữ liệu `refund_ledger` để kiểm tra tính chính xác số tiền hay chính sách. Do đó **không được dùng `helpful` judge làm CI gate**; các tiêu chí liên quan đến tiền phải chấm bằng **code grader** (`RefundAmountCorrect`, `ReplyMatchesLedger`).
- **Tiêu chí được giữ (`tone_ok`):** Ma trận nhầm lẫn `{'tp': 24, 'fp': 4, 'fn': 6, 'tn': 66}` (`κ = 0.757`, `P = 0.857`, `R = 0.800`), đạt cả 3 ngưỡng `FLOORS` (tỉ lệ lỗi hiệu chỉnh Rogan–Gladen = `0.30`), đủ tin cậy để đánh giá sắc thái giao tiếp sau khi hiệu chỉnh các điểm yếu ở rubric trên.
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có held-out thật.
