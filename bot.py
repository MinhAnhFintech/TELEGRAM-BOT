import telebot
from datetime import datetime
from data_provider import get_historical_data, get_vn30_list
from strategy import check_signal

def register_handlers(bot):
    
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "📈 **FINTECH BOT - TÍN HIỆU CHỨNG KHOÁN VN** 📉\n\n"
            "Bot cung cấp tín hiệu Mua/Bán dựa trên Phân tích Kỹ thuật (EMA20, EMA50, RSI).\n\n"
            "Các lệnh khả dụng:\n"
            "🔸 `/check <Mã_CK>`: Xem tín hiệu một mã cụ thể. VD: `/check FPT`\n"
            "🔸 `/signals`: Quét danh sách VN30 để tìm tín hiệu Mua/Bán trong phiên hiện tại.\n"
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown")

    @bot.message_handler(commands=['check'])
    def check_ticker(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập mã cổ phiếu.\nVD: `/check HPG`", parse_mode="Markdown")
            return
            
        ticker = parts[1].upper()
        bot.reply_to(message, f"🔍 Đang phân tích dữ liệu cho **{ticker}**...", parse_mode="Markdown")
        
        df = get_historical_data(ticker)
        
        if df is None:
            bot.reply_to(message, f"❌ Không lấy được dữ liệu cho mã {ticker}. Có thể mã không tồn tại.", parse_mode="Markdown")
            return
            
        signal, close_price, rsi = check_signal(df)
        
        if signal == "NOT_ENOUGH_DATA":
            bot.reply_to(message, "❌ Không đủ dữ liệu lịch sử để phân tích.", parse_mode="Markdown")
            return
            
        emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
        
        # Lấy thời gian hiện tại và thời gian của phiên giao dịch cuối cùng
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        last_trading_date = df.index[-1].strftime('%d/%m/%Y')
        
        reply_text = (
            f"📊 **Kết quả phân tích {ticker}**:\n\n"
            f"• Giá hiện tại: **{close_price}** (VND)\n"
            f"📊 **Kết quả phân tích {ticker}**:\n"
            f"🕒 Cập nhật lúc: {current_time}\n"
            f"📅 Dữ liệu phiên: {last_trading_date}\n\n"
            f"• Giá đóng cửa: **{close_price}** (VND)\n"
            f"• Chỉ số RSI(14): **{rsi}**\n"
            f"• Khuyến nghị: {emoji} **{signal}**\n\n"
            f"_(Lưu ý: Tín hiệu chỉ mang tính chất tham khảo dựa trên EMA và RSI)_"
            f"_(Lưu ý: Tín hiệu chỉ mang tính tham khảo dựa trên TA)_"
        )
        bot.send_message(message.chat.id, reply_text, parse_mode="Markdown")

    @bot.message_handler(commands=['signals'])
    def scan_market(message):
        bot.reply_to(message, "⏳ Đang quét danh sách VN30. Quá trình này có thể mất khoảng 10-20 giây...", parse_mode="Markdown")
        
        vn30 = get_vn30_list()
        buy_list = []
        sell_list = []
        
        for ticker in vn30:
            df = get_historical_data(ticker, days=120) # Lấy 120 ngày cho nhanh hơn khi quét
            if df is not None:
                signal, close_price, _ = check_signal(df)
                if signal == "BUY":
                    buy_list.append(f"{ticker} ({close_price})")
                elif signal == "SELL":
                    sell_list.append(f"{ticker} ({close_price})")
                    
        reply_text = "🎯 **TỔNG HỢP TÍN HIỆU VN30 HÔM NAY** 🎯\n\n"
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        
        reply_text = f"🎯 **TỔNG HỢP TÍN HIỆU VN30** 🎯\n"
        reply_text += f"🕒 Thời gian quét: {current_time}\n\n"
        
        reply_text += "🟢 **TÍN HIỆU MUA (BUY):**\n"
        if buy_list:
            reply_text += ", ".join(buy_list) + "\n\n"
        else:
            reply_text += "Không có tín hiệu Mua nào.\n\n"
            
        reply_text += "🔴 **TÍN HIỆU BÁN (SELL):**\n"
        if sell_list:
            reply_text += ", ".join(sell_list) + "\n"
        else:
            reply_text += "Không có tín hiệu Bán nào.\n"
            
        bot.send_message(message.chat.id, reply_text, parse_mode="Markdown")

