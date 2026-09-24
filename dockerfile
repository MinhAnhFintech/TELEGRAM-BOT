FROM python:3.10-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Không tạo file .pyc và hiển thị log ngay lập tức
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Cài đặt các gói hệ thống cần thiết (ví dụ fonts cho biểu đồ matplotlib nếu cần)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements vào container để tận dụng cache layer
COPY requirements.txt .

# Nâng cấp pip và cài đặt thư viện
# (Bổ sung matplotlib và mplfinance vì chart_generator.py sử dụng nhưng không có trong requirements.txt)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir matplotlib mplfinance

# Copy toàn bộ mã nguồn vào container
COPY . .

# Tạo thư mục đầu ra cho biểu đồ để tránh lỗi khi bot chạy
RUN mkdir -p data/output

# Chạy bot
CMD ["python", "main.py"]
