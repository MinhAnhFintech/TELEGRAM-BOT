# 📈 Fintech Bot - Trợ Lý Đầu Tư Chứng Khoán Trí Tuệ Nhân Tạo

Đây là dự án Telegram Bot chuyên sâu, tự động sàng lọc cổ phiếu, phát hiện cơ hội và quản trị rủi ro trên thị trường chứng khoán Việt Nam. Bot không dùng mô hình dự báo tương lai ảo mà hoạt động dựa trên các nguyên tắc **Phân tích Kỹ thuật (Technical Analysis)** và **Phân tích Cơ bản (Fundamental Analysis)** cực kỳ khắt khe theo khung logic chuyên nghiệp.

## 1. Tính năng nổi bật & Cấu trúc Mô hình

### A. Luồng Dữ Liệu Tốc Độ Cao (Realtime API)
- **Truy xuất trực tiếp API VNDirect:** Cào dữ liệu lịch sử giá, BCTC, P/E, EPS, Lợi suất cổ tức,... trực tiếp từ máy chủ VNDirect chỉ trong **~1 giây**, độ trễ cực thấp, không bị chặn bởi tường lửa Cloudflare.
- **Hệ thống Adapter linh hoạt:** Hỗ trợ quét thị trường qua luồng API phụ của DNSE hoặc TCBS.

### B. Cơ chế Phân loại và Cổng bảo vệ (Gate)
- **Kiểm tra Gate (Chốt chặn an toàn):** Loại bỏ lập tức (KHÔNG KHUYẾN NGHỊ) các cổ phiếu rác, vốn chủ sở hữu âm (BVPS <= 0), hoặc thanh khoản 20 phiên dưới 1 tỷ VNĐ/ngày.
- **Phân loại Ngành (Sector Classification):** Tự động phân luồng mã vào 3 nhóm ngành chính: `FINANCE (Tài chính)`, `REAL_ESTATE (Bất động sản)`, và `GENERAL (Đa ngành)` để áp dụng tiêu chuẩn phân tích phù hợp.

### C. Bộ 3 Chiến Lược Đầu Tư Lõi (CL1, CL2, CL3)
Người dùng có thể chọn chiến lược ưu tiên qua lệnh `/setup`:
1. **CL1 - Trading Ngắn Hạn (< 3 Tháng):** Lướt sóng theo dòng tiền. Bắt tín hiệu MUA khi RSI 50-70, EMA20 cắt lên EMA50 và Vol > 1.2 lần trung bình. Chốt lời (R/R > 2), cắt lỗ khắt khe.
2. **CL2 - Tăng Trưởng & Dòng Tiền (3 - 12 Tháng):** Lọc BCTC (EPS dương, ROE > 10%). Điểm MUA vọt đỉnh Pivot 20 phiên kèm khối lượng đột biến (>1.5 lần trung bình).
3. **CL3 - Giá Trị & Cổ Tức (> 12 Tháng):** Tìm kiếm tích sản giá rẻ. Định giá P/E < 15, Dividend Yield >= 3%. Bắt đáy khi giá rớt về mức thấp nhất 120 ngày hoặc đâm thủng dải dưới Bollinger Band, chờ xác nhận nến đảo chiều.

### D. Hệ thống Khuyến Nghị Tổng Hợp & Chấm Điểm AI SmartCore
- Tự động đối chiếu chéo kết quả 3 chiến lược để ra kết luận cuối cùng (🔥 MUA MẠNH, 🟢 MUA, 👀 HOLD/THEO DÕI, ⚠️ GIẢM TỶ TRỌNG, 🔴 BÁN).
- **AI SmartCore:** Thuật toán tự động chấm điểm cổ phiếu thang 10, đánh giá toàn diện 4 mặt: Định giá (P/E), Nền tảng (ROE), Kỹ thuật (Trend EMA) và Dòng tiền (Khối lượng), xếp hạng từ Hạng A (Xuất sắc) đến Hạng D (Yếu).

### E. Cá nhân hóa & Lưu trữ vĩnh viễn (Persistence)
- Hệ thống hỗ trợ đa người dùng (Multi-users). Lựa chọn ưu tiên của mỗi người qua lệnh `/setup` sẽ được ghi nhớ vĩnh viễn vào file cục bộ `user_settings.json`.
- Ngay cả khi sập nguồn hoặc khởi động lại server, cấu hình bot của bạn vẫn được giữ nguyên (không bị reset về mặc định).

---

## 2. Hướng dẫn cài đặt

### Bước 1: Môi trường & Thư viện
Dự án yêu cầu Python 3.10 trở lên.
Mở Terminal tại thư mục gốc và chạy:
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Bước 2: Bảo mật Bot Token với `.env`
1. Tìm `@BotFather` trên ứng dụng Telegram, gõ `/newbot` để tạo bot và lấy **HTTP API Token**.
2. Tạo một file tên là `.env` trong thư mục gốc của dự án.
3. Nhập token vào file `.env` với định dạng:
   ```env
   BOT_TOKEN=MÃ_TOKEN_CỦA_BẠN_LẤY_TỪ_BOTFATHER
   ```

### Bước 3: Khởi chạy
Chạy bot bằng lệnh:
```bash
python main.py
```
Hệ thống có cơ chế tự động thử lại (Anti-Crash) nếu kết nối với máy chủ Telegram bị chập chờn.

---

## 3. Các Lệnh Telegram Hỗ Trợ
Vào Telegram, mở khung chat với bot của bạn và trải nghiệm:
- ⚙️ `/setup` : Mở Menu thiết lập Chiến lược đầu tư (Lướt sóng / Tăng trưởng / Tích sản).
- 🔍 `/xem <Mã_CK>` (hoặc `/check`) : Trả về báo cáo phân tích toàn diện, render linh hoạt và gọn gàng theo đúng chiến lược bạn đã setup. *(VD: `/xem FPT`)*
- 🎯 `/signals` : Quét nhanh tín hiệu rổ VN30.
- 🔄 `/switch <Sàn>` : Đổi nguồn dữ liệu dự phòng quét thị trường (DNSE / TCBS).
