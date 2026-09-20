import sys
import telebot
import os

# Khắc phục lỗi in Unicode trên Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from bot import register_handlers
from dotenv import load_dotenv

def main():
    # Load biến môi trường từ file .env
    load_dotenv()
    
    # Lấy token từ .env
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ LỖI: Không tìm thấy BOT_TOKEN. Vui lòng kiểm tra file .env!")
        return
        
    bot = telebot.TeleBot(BOT_TOKEN)
    
    # Đăng ký các lệnh (commands) từ module bot.py
    register_handlers(bot)
    
    print("🚀 Fintech Bot Chứng Khoán VN đang khởi động...")
    print("Đang lắng nghe tin nhắn từ Telegram...")
    
    import time
    import requests
    
    # Vòng lặp chống crash bot khi đứt mạng / timeout từ Telegram
    while True:
        try:
            # Bỏ qua các tin nhắn cũ khi bot offline, tăng timeout để tránh lỗi ReadTimeout
            bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
            break
        except requests.exceptions.ReadTimeout:
            print("⏳ Mạng chậm, bị timeout kết nối tới Telegram. Đang tự động thử lại sau 3 giây...")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Lỗi mất kết nối: {e}. Đang tự động kết nối lại...")
            time.sleep(3)

if __name__ == "__main__":
    main()
