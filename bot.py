import telebot
from datetime import datetime
from data.data_provider import get_historical_data, get_vn30_list, switch_exchange, get_current_exchange
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
            "🔸 `/switch <Sàn>`: Chuyển đổi nguồn dữ liệu (VD: `/switch DNSE` hoặc `/switch TCBS`).\n"
            f"\n_Nguồn dữ liệu hiện tại: {get_current_exchange()}_"
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown")

    @bot.message_handler(commands=['switch'])
    def switch_exchange_command(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập tên sàn (DNSE hoặc TCBS).\nVD: `/switch TCBS`", parse_mode="Markdown")
            return
            
        exchange = parts[1].upper()
        try:
            switch_exchange(exchange)
            bot.reply_to(message, f"✅ Đã chuyển nguồn dữ liệu sang **{exchange}** thành công!", parse_mode="Markdown")
        except ValueError as e:
            bot.reply_to(message, f"❌ {e}", parse_mode="Markdown")

    @bot.message_handler(commands=['check', 'xem'])
    def check_ticker(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập mã cổ phiếu.\nVD: `/check HPG`", parse_mode="Markdown")
            return
            
        ticker = parts[1].upper()
        print(f"Đang phân tích tín hiệu AI SmartCore cho mã: {ticker}")
        
        # Gửi tin nhắn thông báo đang xử lý
        processing_msg = bot.reply_to(message, f"🔍 Đang thu thập dữ liệu và tính điểm AI SmartCore cho **{ticker}**...", parse_mode="Markdown")
        
        try:
            from bot_logic import analyze_stock
            result_text = analyze_stock(ticker)
            
            # Cập nhật tin nhắn đang xử lý bằng kết quả thực tế
            bot.edit_message_text(
                chat_id=message.chat.id, 
                message_id=processing_msg.message_id, 
                text=result_text, 
                parse_mode="Markdown"
            )
        except Exception as e:
            bot.edit_message_text(
                chat_id=message.chat.id, 
                message_id=processing_msg.message_id, 
                text=f"❌ Không thể phân tích mã {ticker}. Lỗi: {str(e)}", 
                parse_mode="Markdown"
            )

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

