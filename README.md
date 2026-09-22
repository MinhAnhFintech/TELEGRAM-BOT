# 🤖 HỆ THỐNG AI AGENT TƯ VẤN ĐẦU TƯ CHỨNG KHOÁN (V3 - VERSION)

Dự án này là một hệ thống Bot Telegram tích hợp AI Agent hoạt động như một hệ chuyên gia (Rule-based Expert System). Hệ thống tự động thu thập dữ liệu thời gian thực, xử lý và đưa ra tín hiệu giao dịch tuân thủ tuyệt đối các nguyên tắc quản trị rủi ro khắt khe nhất trong cuốn sách *"Chiến Lược Đầu Tư Chứng Khoán - Phương Pháp và Chiến Thuật Thành Công"*.

---

## 🌟 TÍNH NĂNG NỔI BẬT

- **Hệ thống 3 Bước Sàng lọc (3-Step Engine):** Lọc Cổ phiếu (Screener) -> Tìm điểm ra vào lệnh (Timing) -> Quản trị rủi ro & Danh mục (Risk Management).
- **Bộ 3 Thuật toán Chiến lược chuyên sâu (V3):**
  - **`CL1` (Momentum Agent - < 3 Tháng):** Đầu cơ theo đà tăng trưởng. Kích hoạt khi MACD chớm dương, RSI > 50, Volume bùng nổ > 1.5 lần. Bảo vệ bằng **Trailing Stop 10%**.
  - **`CL2` (CANSLIM Agent - 3 đến 12 Tháng):** Đánh Breakout nền giá. Điều kiện cực gắt: Giá phải vượt và nằm TRÊN đường SMA50. Kỷ luật **Cut loss tuyệt đối 7.5%**.
  - **`CL3` (Value Investing - > 12 Tháng):** Bắt đáy cổ phiếu giá trị (P/E < 15, Cổ tức > 3%). Tín hiệu đảo chiều kinh điển: SMA50 cắt lên SMA200 (Golden Cross) hoặc MACD dương tại vùng đáy 1 năm. Giới hạn **Max Loss 20%**.
- **Module Backtest Tích hợp Chuyên nghiệp:** Khả năng kiểm thử chiến lược (Backtest) bằng data thực tế lên đến hàng chục năm. Đã mô phỏng trượt giá (khớp lệnh giá mở cửa hôm sau) và tính toán đầy đủ Thuế + Phí giao dịch (0.4%/lệnh).
- **Chấm điểm AI SmartCore (1 - 10):** Chấm điểm tự động sức khoẻ doanh nghiệp dựa trên (P/E, P/B, ROE, Net Margin, D/E).
- **Vẽ biểu đồ tương tác (Chart Generator):** Tự động render biểu đồ Nến Nhật sạch sẽ với SMA50, SMA200, MACD, RSI và các điểm MUA/BÁN được vẽ trực tiếp trên hình.

---

## 🛠 KIẾN TRÚC HỆ THỐNG & CÔNG NGHỆ

- **Ngôn ngữ:** Python 3.10+
- **Thư viện lõi:**
  - `pyTelegramBotAPI`: Quản lý giao tiếp người dùng qua Telegram.
  - `vnstock` / `vnai`: Thu thập dữ liệu chứng khoán (BCTC, Ohlcv, Tỉ số tài chính).
  - `pandas`, `numpy`: Xử lý Dataframe, thiết kế Engine Backtest và tính toán (SMA, MACD, RSI, ATR).
  - `matplotlib`, `mplfinance`: Engine vẽ biểu đồ chứng khoán.

---

## 📜 CÁC LỆNH (COMMANDS) CỦA BOT TRÊN TELEGRAM

| Lệnh | Chức năng |
|---|---|
| `/start` | Khởi động Bot, hiển thị lời chào và hướng dẫn. |
| `/help` | Xem danh sách toàn bộ các lệnh. |
| `/check <mã>` | Phân tích toàn diện 1 mã cổ phiếu. Trả về Khuyến nghị (MUA/BÁN), thông số Cắt lỗ/Chốt lời, Tỷ lệ Margin + Nút bấm xem biểu đồ. |
| `/chart <mã>` | Vẽ và gửi ngay hình ảnh phân tích kỹ thuật của cổ phiếu theo Chiến lược đang chọn. |
| `/signals` | Quét toàn bộ rổ VN30 để lọc ra các mã đang có tín hiệu MUA. |
| `/setup` | Mở menu cài đặt Chiến lược cá nhân hóa (CL1 / CL2 / CL3). |
| `/why` | Hiển thị bảng giải thích cơ chế chấm điểm của AI SmartCore. |

---

## 🔬 MODULE BACKTEST (MỚI)

Để chứng minh tính hiệu quả của Thuật toán, dự án đi kèm một công cụ Backtest độc lập tại file `backtest.py`.

**Cách chạy Backtest:**
Mở Terminal / Command Prompt và chạy lệnh sau:
```bash
# Backtest FPT chiến lược CL3 trong 1500 ngày qua
python backtest.py --symbol FPT --strategy CL3 --days 1500

# Backtest VNM chiến lược CL1 trong 1000 ngày
python backtest.py --symbol VNM --strategy CL1 --days 1000
```
**Các chỉ số Backtest tự động xuất ra:**
- Số lượng lệnh (Total Trades), Tỷ lệ thắng (Win Rate).
- Lãi trung bình lệnh thắng / Lỗ trung bình lệnh thua (Reward/Risk Ratio).
- Lợi nhuận gộp (Net PNL), Tỷ suất sinh lời (ROI).
- **Max Drawdown (Mức sụt giảm tối đa)** - Thể hiện khả năng quản trị rủi ro của AI Agent.
- So sánh hiệu quả với chiến lược Mua và Giữ (Buy & Hold).

---

## 🔐 HƯỚNG DẪN CÀI ĐẶT BOT

1. Yêu cầu hệ thống đã cài đặt Python 3.10 trở lên.
2. Chạy môi trường ảo: `.\venv\Scripts\activate` (trên Windows).
3. Cài đặt thư viện: `pip install -r requirements.txt`
4. Cấu hình file `.env`: Điền Token lấy từ BotFather vào biến `BOT_TOKEN`.
5. Chạy Bot: `python main.py`

---
*Dự án thuộc khuôn khổ Đồ án Hệ thống Giao dịch Tự động & Phân tích Đầu tư Ứng dụng AI.*
