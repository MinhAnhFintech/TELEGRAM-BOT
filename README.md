# 🤖 HỆ THỐNG BOT TELEGRAM TƯ VẤN ĐẦU TƯ CHỨNG KHOÁN TỰ ĐỘNG

Dự án này là một hệ thống Bot Telegram cung cấp giải pháp phân tích và tư vấn đầu tư chứng khoán toàn diện. Hệ thống thu thập dữ liệu thời gian thực, xử lý bằng các thuật toán kỹ thuật (Technical Analysis) và cơ bản (Fundamental Analysis), từ đó đưa ra tín hiệu giao dịch theo các chiến lược cá nhân hóa.

---

## 🌟 TÍNH NĂNG NỔI BẬT

- **Dữ liệu chuẩn xác 100%:** Lấy dữ liệu Real-time (OHLCV) và Báo cáo tài chính trực tiếp từ các công ty chứng khoán (qua thư viện Vnstock).
- **Phân tích đa khung - 3 Chiến lược riêng biệt:**
  - `CL1` (Đầu cơ Ngắn hạn < 3 Tháng): Theo dấu dòng tiền, điểm cắt EMA, RSI.
  - `CL2` (Tăng trưởng Trung hạn 3-12 Tháng): Breakout đỉnh 20 phiên, ROE > 10, EPS dương.
  - `CL3` (Giá trị & Cổ tức > 12 Tháng): Bắt đáy hỗ trợ dài hạn (Bollinger Bands), lợi suất cổ tức > 3%.
- **Chấm điểm AI SmartCore (1 - 10):** Tự động tổng hợp và chấm điểm sức khoẻ doanh nghiệp, xếp loại từ hạng A (Xuất sắc) đến hạng D (Yếu).
- **Quản trị rủi ro chuyên nghiệp:**
  - Khuyến nghị tỷ trọng sử dụng đòn bẩy (Margin) tự động dựa trên Xu hướng, D/E và RSI.
  - Tính toán **Stop Loss (Cắt lỗ)** và **Target Price (Chốt lời)** ĐỘNG bằng chỉ báo biến động ATR (Average True Range) – không dùng % cố định cứng nhắc. (Đồng thời hỗ trợ cả 2 vị thế Long/Short).
- **Vẽ biểu đồ tương tác (Chart Generator):** Tự động render biểu đồ Nến Nhật chuyên nghiệp (tương tự TradingView) với Fibonacci, EMA20/50, Bollinger Bands và các điểm MUA/BÁN trực quan.

---

## 🛠 KIẾN TRÚC HỆ THỐNG & CÔNG NGHỆ

- **Ngôn ngữ:** Python 3.10+
- **Thư viện lõi:**
  - `pyTelegramBotAPI`: Quản lý webhook và giao tiếp với Telegram.
  - `vnstock` / `vnai`: Lõi thu thập dữ liệu chứng khoán Việt Nam (BCTC, Dữ liệu giá, P/E, ROE).
  - `pandas`, `numpy`: Xử lý mảng và tính toán các chỉ báo kỹ thuật (EMA, RSI, ATR).
  - `matplotlib`, `mplfinance`: Engine vẽ biểu đồ chứng khoán.
- **Mẫu thiết kế (Design Patterns):** 
  - *Adapter Pattern*: Hệ thống chuyển đổi linh hoạt các nguồn cấp dữ liệu (DNSE -> VNDirect -> KBS) để đảm bảo không bao giờ bị đứt gãy data.

---

## 📜 CÁC LỆNH (COMMANDS) CỦA BOT

| Lệnh | Chức năng |
|---|---|
| `/start` | Khởi động Bot, hiển thị lời chào và hướng dẫn. |
| `/help` | Xem danh sách toàn bộ các lệnh. |
| `/check <mã>` | Phân tích toàn diện 1 mã cổ phiếu (Kỹ thuật, Cơ bản, BCTC, Tín hiệu MUA/BÁN). Trả về văn bản + Nút bấm xem biểu đồ. |
| `/chart <mã>` | Vẽ và gửi ngay hình ảnh phân tích kỹ thuật của mã cổ phiếu. |
| `/signals` | Quét toàn bộ rổ VN30 để lọc ra các mã đang có tín hiệu MUA hiện tại. |
| `/setup` | Mở menu cài đặt Chiến lược cá nhân hóa (CL1 / CL2 / CL3). |
| `/why` | Hiển thị bảng giải thích cơ chế chấm điểm của AI SmartCore (Tại sao cộng điểm, tại sao trừ điểm). |

---

## 📊 VÍ DỤ VỀ LUỒNG HOẠT ĐỘNG (WORKFLOW)

**Kịch bản Người dùng muốn kiểm tra mã FPT:**

1. **Bước 1:** Gõ lệnh `/check FPT` trên Telegram.
2. **Bước 2 (Xử lý nền):** Bot tải 120 phiên giá gần nhất + Báo cáo tài chính Quý mới nhất của FPT từ Vnstock. Tính toán các đường trung bình (EMA), sức mạnh tương đối (RSI), và biến động giá (ATR).
3. **Bước 3 (Đánh giá):** Bot kiểm tra FPT qua "Gate" (Thanh khoản > 1 Tỷ/ngày, Vốn chủ > 0). Chấm điểm AI dựa trên (P/E, ROE, Net Margin, D/E).
4. **Bước 4 (Khuyến nghị):** Bot trả về tin nhắn Telegram khuyên `BÁN` / `MUA` / `GIỮ`, kèm các thông số (SL/TP, Margin) và nút bấm **"📊 Xem biểu đồ Kỹ thuật"**.
5. **Bước 5 (Trực quan hóa):** Người dùng bấm nút. Module `chart_generator.py` được gọi, render hình ảnh đồ thị Nến trắng nền sạch, có vẽ rõ Fibonacci và vị trí chốt lời/cắt lỗ (SL/TP) rồi gửi lại cho người dùng.

---

## 🔐 HƯỚNG DẪN CÀI ĐẶT

1. Yêu cầu hệ thống đã cài đặt Python.
2. Chạy môi trường ảo: `.\venv\Scripts\activate` (trên Windows).
3. Cài đặt thư viện: `pip install -r requirements.txt`
4. Cấu hình file `.env`: Thay thế `BOT_TOKEN` bằng token lấy từ BotFather.
5. Chạy Bot: `python main.py`

---
*Dự án thuộc khuôn khổ Đồ án/Bài tập Phân tích Đầu tư Chứng khoán Ứng dụng AI.*
