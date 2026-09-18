# 📈 Fintech Bot - Tín Hiệu Đầu Tư Chứng Khoán Việt Nam

Đây là dự án Telegram Bot tự động phân tích và cung cấp tín hiệu Mua/Bán cổ phiếu trên thị trường chứng khoán Việt Nam, dựa trên **Phân tích Kỹ thuật (Technical Analysis)**.

## 1. Tính năng nổi bật
- **Luồng dữ liệu (Data Pipeline):** Tự động cào dữ liệu lịch sử giá và khối lượng từ TCBS API (Dữ liệu EOD/Realtime nhanh chóng và ổn định).
- **Core Logic (Triết lý đầu tư):** Sử dụng các chỉ báo kỹ thuật cốt lõi:
  - Exponential Moving Average (EMA 20 & EMA 50)
  - Relative Strength Index (RSI)
- **Tín hiệu Mua (BUY):** Giao cắt vàng (Golden Cross) khi EMA 20 cắt lên EMA 50, kết hợp RSI > 50 (xu hướng tăng được xác nhận).
- **Tín hiệu Bán (SELL):** Giá đóng cửa thủng đường hỗ trợ động EMA 50, hoặc RSI có dấu hiệu tạo đỉnh ở vùng quá mua (>70) và cắt xuống.
- **Tính năng Quét (Scanner):** Khả năng quét toàn bộ rổ VN30 để lọc ra các cổ phiếu đang có tín hiệu tốt ngay trong ngày.

## 2. Kiến trúc Hệ thống

Dự án được thiết kế theo cấu trúc module (Clean Code):

```text
bot/
│
├── data_provider.py    # Xử lý Data Pipeline: Kết nối TCBS API, chuẩn hóa Pandas DataFrame.
├── strategy.py         # Xử lý Core Logic: Chứa các công thức toán học tính EMA, RSI.
├── bot.py              # Xử lý User Interface: Đăng ký các lệnh Telegram (/check, /signals).
├── main.py             # Entry Point: Khởi chạy ứng dụng.
├── requirements.txt    # Danh sách thư viện.
└── README.md           # Tài liệu dự án.
```

## 3. Sơ đồ Luồng Dữ liệu (Data Flow)

1. Người dùng gõ lệnh (VD: `/check HPG`) trên Telegram.
2. Bot nhận lệnh và gọi hàm `get_historical_data('HPG')` từ `data_provider.py`.
3. `data_provider.py` gọi HTTP GET đến `TCBS API`, nhận về JSON, chuyển thành `Pandas DataFrame`.
4. Dữ liệu được đẩy vào `strategy.py`. Tại đây, thuật toán tính toán `EMA_20`, `EMA_50`, `RSI_14` và đưa ra quyết định dựa trên điều kiện logic.
5. `bot.py` định dạng kết quả và gửi trả lại thông báo cho người dùng trên Telegram.

## 4. Hướng dẫn cài đặt và sử dụng

### Bước 1: Cài đặt thư viện
Yêu cầu Python 3.10+ (Đã thử nghiệm thành công với các bản mới nhất).
Mở Terminal tại thư mục gốc và chạy:
```bash
pip install -r requirements.txt
```

### Bước 2: Cấu hình Bot Token
1. Tìm `@BotFather` trên Telegram và tạo bot mới bằng lệnh `/newbot`.
2. Lấy **API Token**.
3. Mở file `main.py`, thay thế đoạn `ĐIỀN_TOKEN_CỦA_BẠN_VÀO_ĐÂY` bằng token của bạn.

### Bước 3: Khởi chạy
```bash
python main.py
```
*(Nếu bạn dùng môi trường ảo `venv`, hãy chạy `.\venv\Scripts\python main.py`)*

### Bước 4: Tương tác
Vào ứng dụng Telegram, chat với bot của bạn bằng các lệnh:
- `/start` hoặc `/help` để xem menu.
- `/check <Mã_CK>` (VD: `/check FPT`): Xem tín hiệu của một mã.
- `/signals`: Quét danh sách VN30 lấy tín hiệu hiện tại.

