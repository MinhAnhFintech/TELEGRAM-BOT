import telebot
import os
from bot import register_handlers

def main():
    # Thay thế bằng token thực tế của bạn hoặc dùng biến môi trường
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8690941059:AAFXSEp11BkrqxwsjpXObGV_LMVa35EqF0k')
    
    if BOT_TOKEN == '8690941059:AAFXSEp11BkrqxwsjpXObGV_LMVa35EqF0k':
        print("⚠️ CẢNH BÁO: Vui lòng thay thế BOT_TOKEN trong file main.py bằng token lấy từ BotFather!")
        
    bot = telebot.TeleBot(BOT_TOKEN)
    
    # Đăng ký các lệnh (commands) từ module bot.py
    register_handlers(bot)
    
    print("🚀 Fintech Bot Chứng Khoán VN đang khởi động...")
    print("Đang lắng nghe tin nhắn từ Telegram...")
    # Bỏ qua các tin nhắn cũ khi bot offline
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    main()
