# Macro textbook (Control Lane)

Khung giáo khoa ngắn. Dùng để **phân trụ** sự kiện trong Fact Pack. Không dùng để đoán Fed/ECB hay giá cặp.

## 1. Ngân hàng trung ương quản lý gì?

Mục tiêu điển hình (Fed, ECB, BoE — gần với 4 đồng chính):

1. **Việc làm / hoạt động** — labor, GDP, PMI  
2. **Ổn định giá** — CPI, PCE, PPI, đôi khi AHE (lương)

Họ **không** tối ưu tỷ giá trong sách giáo khoa chuẩn (trừ khi pack có sự kiện FX/intervention).  
Lãi suất điều hành là công cụ. Pack **không** có đường lãi suất tương lai — cấm bịa path.

## 2. Cách đọc một print

```text
previous  →  forecast  →  actual
  kỳ trước     bias đã priced    bài test
```

- `forecast ≠ previous` = thị trường đã đổi chuyện **trước** giờ G.  
- `actual` trống = chưa test.  
- `actual` vs `forecast` = surprise. Chỉ so trên **cùng fact_id**.  
- Không đặt ngưỡng khác (30K, 50.0) nếu pack không có số đó.

## 3. Bốn trụ

| Trụ | Sự kiện điển hình | A > F (textbook) |
|---|---|---|
| Labor | NFP, Employment Change, UER*, AHE | Labor mạnh hơn consensus (*UER ngược: A > F = yếu hơn) |
| Inflation | CPI, Core CPI, PCE, PPI | Giá nóng hơn consensus |
| Growth | GDP, PMI | Hoạt động mạnh hơn consensus |
| Policy | Rate, statement, press | Số rate: A > F = hawkish hơn consensus. Speech không có số → không chấm tone |

## 4. Tương tác bắt buộc (không giữ mọi câu chuyện)

**Dual mandate:** không thể vừa “labor quá mạnh cần giữ hawkish” vừa “lạm phát đã xong, sắp nới” nếu **cả hai** print cùng tuần đều hot hơn F. Một trong hai narrative phải nới.

**Bộ ba bất khả thi (Mundell–Fleming):** không thể cùng lúc (1) chính sách tiền tệ độc lập, (2) tỷ giá neo/ổn định, (3) dòng vốn tự do. Trong repo này chỉ dùng khi tuần có **policy red** JPY/CNY/EUR — gọi tên căng thẳng, không chấm điểm, không gọi can thiệp.

**Cặp tiền:** Forex là hiệu. Tin USD không tự thành câu chuyện EUR nếu EUR không có red.

## 5. Việc của trader (không phải của model)

Tin red = giờ **test** giả thuyết. Không đặt lệnh swing chính mới trong cửa sổ đó. Giá sau print do người đọc chart — model không có nến.
