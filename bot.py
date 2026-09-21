import telebot
import json
import os
from datetime import datetime
from data.data_provider import get_historical_data, get_vn30_list, switch_exchange, get_current_exchange
from strategy import check_signal

# Lưu trữ chiến lược chính của người dùng vào file để không bị mất khi reset bot
SETTINGS_FILE = 'user_settings.json'

def load_user_strategies():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_user_strategies(data):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

user_strategies = load_user_strategies()

def register_handlers(bot):
    
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = (
            "🤖 **FINTECH BOT - TÍN HIỆU CHỨNG KHOÁN VN** 🤖\n\n"
            "Bot cung cấp tín hiệu Mua/Bán dựa trên Phân tích Kỹ thuật và Cơ bản.\n\n"
            "Các lệnh khả dụng:\n"
            "⚙️ `/setup`: Cài đặt thời gian đầu tư.\n"
            "🔍 `/check <Mã>` (hoặc `/xem`): Phân tích chi tiết 1 mã. VD: `/check FPT`\n"
            "📊 `/chart <Mã>`: Vẽ biểu đồ Nến + Fibonacci + Tín hiệu. VD: `/chart HPG`\n"
            "📈 `/signals`: Quét danh sách VN30 để tìm tín hiệu.\n"
            "🧠 `/why`: Xem cách AI chấm điểm cổ phiếu.\n"
            "🔄 `/switch <Sàn>`: Chuyển đổi nguồn dữ liệu (TCBS, DNSE)."
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown")

    @bot.message_handler(commands=['setup'])
    def setup_command(message):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("Dưới 3 tháng (Lướt sóng)", callback_data="setup_CL1"))
        markup.add(telebot.types.InlineKeyboardButton("Từ 3-12 tháng (Tăng trưởng)", callback_data="setup_CL2"))
        markup.add(telebot.types.InlineKeyboardButton("Trên 12 tháng (Giá trị)", callback_data="setup_CL3"))
        
        text = (
            "⚙️ **CÀI ĐẶT CHIẾN LƯỢC ĐẦU TƯ**\n"
            "Vui lòng chọn khoảng thời gian nắm giữ mong muốn. Bot sẽ tự động điều chỉnh **Khuyến nghị cuối cùng** dựa trên chiến lược này:"
        )
        bot.reply_to(message, text, reply_markup=markup, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('setup_'))
    def callback_setup(call):
        strategy = call.data.split('_')[1]
        chat_id = str(call.message.chat.id)  # Json yêu cầu key là string
        user_strategies[chat_id] = strategy
        save_user_strategies(user_strategies)
        
        names = {
            "CL1": "Dưới 3 tháng (Kỹ thuật ngắn hạn)", 
            "CL2": "Từ 3-12 tháng (Cơ bản + Dòng tiền)", 
            "CL3": "Trên 12 tháng (Giá trị + Cổ tức)"
        }
        bot.answer_callback_query(call.id, f"Đã lưu: {names[strategy]}")
        bot.edit_message_text(
            f"✅ **THIẾT LẬP THÀNH CÔNG**\n\nBạn đã chọn chiến lược cốt lõi: **{names[strategy]}**.\n"
            f"Từ giờ, lệnh `/xem` sẽ tổng hợp Khuyến nghị (MUA/BÁN/HOLD) ưu tiên theo chiến lược này.", 
            call.message.chat.id, 
            call.message.message_id, 
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=['why'])
    def explain_criteria(message):
        text = (
            "🤖 **TIÊU CHÍ CHẤM ĐIỂM AI SMARTCORE (Thang 10 điểm)**\n\n"
            "Hệ thống AI tự động chấm điểm cổ phiếu dựa trên sự kết hợp giữa Phân tích Cơ bản (Sức khoẻ tài chính) và Phân tích Kỹ thuật (Dòng tiền):\n\n"
            "**1. ĐỊNH GIÁ & HIỆU QUẢ (Max 5 điểm)**\n"
            "• Định giá P/E (Max 2đ): Rẻ (P/E < 10) +2đ, Hợp lý (10-15) +1đ.\n"
            "• Hiệu quả ROE (Max 3đ): Xuất sắc (> 20%) +3đ, Tốt (> 15%) +2đ, Khá (> 10%) +1đ.\n\n"
            "**2. SỨC KHOẺ TÀI CHÍNH (Max 2 điểm)**\n"
            "• Nợ / Vốn chủ sở hữu (Max 1đ): An toàn (D/E < 1.0) +1đ, Kiểm soát được (1.0 - 2.0) +0.5đ.\n"
            "• Biên lợi nhuận ròng (Max 1đ): Rất cao (> 15%) +1đ, Ổn định (> 5%) +0.5đ.\n\n"
            "**3. XU HƯỚNG & DÒNG TIỀN (Max 3 điểm)**\n"
            "• Xu hướng Giá (Max 1.5đ): Tăng trưởng mạnh (Giá > EMA20 > EMA50) +1.5đ.\n"
            "• Dòng tiền Khối lượng (Max 1.5đ): Dòng tiền lớn vào (Vol > 150% TB 20 phiên) +1.5đ.\n\n"
            "📊 **BẢNG XẾP HẠNG:**\n"
            "⭐ HẠNG A (8-10đ): Cổ phiếu Toàn diện, Sẵn sàng bùng nổ.\n"
            "⭐ HẠNG B (6-8đ): Doanh nghiệp Tốt, Chờ điểm mua kỹ thuật.\n"
            "⚠️ HẠNG C (4-6đ): Trung bình, Rủi ro 50/50.\n"
            "❌ HẠNG D (< 4đ): Yếu kém, Hạn chế giao dịch."
        )
        bot.reply_to(message, text, parse_mode="Markdown")

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
        
        # Lấy chiến lược người dùng đã cấu hình, nếu chưa mặc định là CL1
        chat_id_str = str(message.chat.id)
        main_st = user_strategies.get(chat_id_str, "CL1")
        
        processing_msg = bot.reply_to(message, f"🔍 Đang thu thập dữ liệu và phân tích **{ticker}** theo chiến lược {main_st}...", parse_mode="Markdown")
        
        try:
            from bot_logic import analyze_stock
            result_text = analyze_stock(ticker, main_strategy=main_st)
            
            # Tạo nút bấm "Xem biểu đồ" - truyền chiến lược vào callback
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(
                "📊 Xem biểu đồ Kỹ thuật", 
                callback_data=f"chart_{ticker}_{main_st}"
            ))
            
            bot.edit_message_text(
                chat_id=message.chat.id, 
                message_id=processing_msg.message_id, 
                text=result_text, 
                parse_mode="Markdown",
                reply_markup=markup
            )
        except Exception as e:
            bot.edit_message_text(
                chat_id=message.chat.id, 
                message_id=processing_msg.message_id, 
                text=f"❌ Không thể phân tích mã {ticker}. Lỗi: {str(e)}", 
                parse_mode="Markdown"
            )

    @bot.callback_query_handler(func=lambda call: call.data.startswith('chart_'))
    def callback_chart(call):
        # Format: chart_TICKER_CL1
        parts_data = call.data.split('_')
        ticker = parts_data[1].upper()
        strategy = parts_data[2] if len(parts_data) > 2 else "CL1"
        
        strategy_names = {"CL1": "Dau co ngan han", "CL2": "Tang truong", "CL3": "Gia tri & Co tuc"}
        st_name = strategy_names.get(strategy, "Dau co")
        
        bot.answer_callback_query(call.id, f"📊 Đang vẽ biểu đồ {ticker} ({st_name})...")
        
        try:
            from chart_generator import generate_trading_chart
            filepath = generate_trading_chart(ticker, strategy=strategy)
            
            if filepath and os.path.exists(filepath):
                captions = {
                    "CL1": f"📊 {ticker} - CL1: Đầu cơ ngắn hạn\n▲ LONG (Mua vào) | ▼ SHORT (Bán khống)\nSL/TP cụ thể trên biểu đồ | Dữ liệu thực",
                    "CL2": f"📊 {ticker} - CL2: Tăng trưởng & Dòng tiền\n▲ MUA khi vượt Pivot 20D + Volume đột biến\nFibonacci + SL/TP | Dữ liệu thực",
                    "CL3": f"📊 {ticker} - CL3: Giá trị & Cổ tức dài hạn\n▲ Bắt đáy khi nến đảo chiều gần BB dưới\nBollinger Bands + Fibonacci | Dữ liệu thực",
                }
                with open(filepath, 'rb') as photo:
                    bot.send_photo(
                        call.message.chat.id, 
                        photo, 
                        caption=captions.get(strategy, captions["CL1"])
                    )
            else:
                bot.send_message(call.message.chat.id, f"❌ Không thể vẽ biểu đồ cho {ticker}.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Lỗi vẽ biểu đồ: {str(e)}")

    @bot.message_handler(commands=['chart'])
    def send_chart(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ Vui lòng nhập mã cổ phiếu.\nVD: `/chart HPG`", parse_mode="Markdown")
            return
        
        ticker = parts[1].upper()
        processing_msg = bot.reply_to(message, f"📊 Đang vẽ biểu đồ cho **{ticker}**... (5-10 giây)", parse_mode="Markdown")
        
        try:
            from chart_generator import generate_trading_chart
            filepath = generate_trading_chart(ticker)
            
            if filepath and os.path.exists(filepath):
                with open(filepath, 'rb') as photo:
                    bot.send_photo(
                        message.chat.id, 
                        photo, 
                        caption=f"📊 {ticker} - Biểu đồ Nến Nhật + EMA + Fibonacci + Tín hiệu MUA/BÁN"
                    )
                # Xóa tin nhắn "đang vẽ"
                bot.delete_message(message.chat.id, processing_msg.message_id)
            else:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=processing_msg.message_id,
                    text=f"❌ Không thể lấy dữ liệu để vẽ biểu đồ cho mã {ticker}."
                )
        except Exception as e:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text=f"❌ Lỗi vẽ biểu đồ cho {ticker}: {str(e)}"
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

