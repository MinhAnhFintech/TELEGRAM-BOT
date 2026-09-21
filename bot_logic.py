import pandas as pd
import numpy as np
import sys
import requests
from datetime import datetime, timedelta

# Khắc phục lỗi in Unicode trên Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


# ═══════════════════════════════════════════════════════════════
# NGUỒN DỮ LIỆU: VNDirect API (nhanh, ổn định, dữ liệu chuẩn)
# ═══════════════════════════════════════════════════════════════

VNDIRECT_HEADERS = {'User-Agent': 'Mozilla/5.0'}
VNDIRECT_TIMEOUT = 8  # seconds


def _vnd_get_ratio(symbol: str, ratio_code: str) -> float:
    """Lấy 1 chỉ số tài chính từ VNDirect API theo ratioCode."""
    try:
        url = f"https://api-finfo.vndirect.com.vn/v4/ratios?q=code:{symbol}~ratioCode:{ratio_code}&size=1&sort=reportDate:DESC"
        r = requests.get(url, headers=VNDIRECT_HEADERS, timeout=VNDIRECT_TIMEOUT)
        data = r.json().get('data', [])
        if data:
            return float(data[0]['value'])
    except Exception:
        pass
    return 0.0


def _kbs_get_bctc_ratios(symbol: str) -> dict:
    """
    Lấy các chỉ số BCTC nâng cao (Net Margin, D/E, ROE, Gross Margin...) từ Vnstock KBS.
    VNDirect /v4/ratios KHÔNG có các trường này nên phải dùng nguồn KBS.
    Trả về dict với key: net_margin, debt_to_equity, gross_margin, roe_kbs
    """
    result = {'net_margin': None, 'debt_to_equity': None, 'gross_margin': None, 'roe_kbs': None}
    try:
        from vnstock.api.financial import Finance
        f = Finance(symbol=symbol, source='KBS')
        ratio = f.ratio(period='quarter', lang='en')
        # Lấy cột quý mới nhất (bỏ cột item, item_id)
        data_cols = [c for c in ratio.columns if c not in ['item', 'item_id']]
        if not data_cols:
            return result
        latest_col = data_cols[0]
        
        # Trích xuất từng chỉ số theo item_id
        for _, row in ratio.iterrows():
            item_id = row.get('item_id', '')
            val = row.get(latest_col)
            try:
                val = float(val) if val is not None else None
            except (ValueError, TypeError):
                val = None
            
            if item_id == 'net_margin':
                result['net_margin'] = val  # Đã là % (VD: 14.81)
            elif item_id == 'debt_to_equity':
                result['debt_to_equity'] = val / 100 if val is not None else None  # API trả % -> chuyển về lần
            elif item_id == 'gross_margin':
                result['gross_margin'] = val
            elif item_id == 'roe':
                result['roe_kbs'] = val
    except Exception as e:
        print(f"[WARN] Lỗi lấy BCTC KBS cho {symbol}: {e}")
    return result


def _vnd_get_stock_price(symbol: str) -> dict:
    """Lấy giá realtime từ VNDirect stock_prices API."""
    try:
        url = f"https://api-finfo.vndirect.com.vn/v4/stock_prices?sort=date&q=code:{symbol}&size=1&page=1"
        r = requests.get(url, headers=VNDIRECT_HEADERS, timeout=VNDIRECT_TIMEOUT)
        data = r.json().get('data', [])
        if data:
            return data[0]
    except Exception:
        pass
    return {}


def _vnd_get_history(symbol: str, days: int = 120) -> pd.DataFrame:
    """Lấy lịch sử giá từ VNDirect stock_prices API (giá đơn vị nghìn đồng, chuẩn)."""
    try:
        url = f"https://api-finfo.vndirect.com.vn/v4/stock_prices?sort=date&q=code:{symbol}&size={days}&page=1"
        r = requests.get(url, headers=VNDIRECT_HEADERS, timeout=VNDIRECT_TIMEOUT)
        data = r.json().get('data', [])
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        # Dùng giá điều chỉnh (ad*) cho chính xác, volume dùng nmVolume
        df2 = pd.DataFrame({
            'date': df['date'],
            'open': pd.to_numeric(df['adOpen'], errors='coerce'),
            'high': pd.to_numeric(df['adHigh'], errors='coerce'),
            'low': pd.to_numeric(df['adLow'], errors='coerce'),
            'close': pd.to_numeric(df['adClose'], errors='coerce'),
            'volume': pd.to_numeric(df['nmVolume'], errors='coerce'),
        })
        df2 = df2.sort_values('date').reset_index(drop=True)
        return df2
    except Exception as e:
        print(f"[WARN] Lỗi lấy lịch sử giá VNDirect: {e}")
        return pd.DataFrame()


def calculate_rsi(data, window=14):
    """Tính toán RSI thủ công bằng pandas."""
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def analyze_stock(symbol: str, main_strategy: str = "CL1") -> str:
    """
    Hàm phân tích mã cổ phiếu và sinh ra chuỗi markdown cho Telegram.
    Toàn bộ dữ liệu lấy từ VNDirect API (nhanh, chính xác, không bị chặn).
    main_strategy: CL1, CL2, hoặc CL3
    """
    symbol = symbol.upper()

    # ═══════════════════════════════════════════════════════════════
    # 1. LẤY DỮ LIỆU LỊCH SỬ GIÁ
    # ═══════════════════════════════════════════════════════════════
    df_hist = _vnd_get_history(symbol, days=120)
    
    if df_hist.empty or len(df_hist) < 3:
        return f"❌ Không thể lấy đủ dữ liệu lịch sử giá cho mã {symbol}."

    df_hist['EMA20'] = df_hist['close'].ewm(span=20, adjust=False).mean()
    df_hist['EMA50'] = df_hist['close'].ewm(span=50, adjust=False).mean()
    df_hist['RSI14'] = calculate_rsi(df_hist, window=14)
    df_hist['Vol_MA20'] = df_hist['volume'].rolling(window=20).mean()

    latest = df_hist.iloc[-1]
    prev = df_hist.iloc[-2]

    current_price = latest['close']       
    price_change_pct = ((current_price - prev['close']) / prev['close']) * 100
    current_vol = latest['volume']
    vol_ma20 = latest['Vol_MA20']
    vol_ratio = (current_vol / vol_ma20) * 100 if vol_ma20 > 0 else 0
    rsi_14 = latest['RSI14']
    ema20 = latest['EMA20']
    ema50 = latest['EMA50']

    # ═══════════════════════════════════════════════════════════════
    # 2. LẤY DỮ LIỆU TÀI CHÍNH TỪ VNDIRECT API
    # ═══════════════════════════════════════════════════════════════
    pe = _vnd_get_ratio(symbol, 'PRICE_TO_EARNINGS')
    pb = _vnd_get_ratio(symbol, 'PRICE_TO_BOOK')
    market_cap_raw = _vnd_get_ratio(symbol, 'MARKETCAP')
    market_cap = market_cap_raw / 1e9 if market_cap_raw > 1e6 else market_cap_raw
    bvps = _vnd_get_ratio(symbol, 'BVPS_CR')
    
    div_yield_val = _vnd_get_ratio(symbol, 'DIVIDEND_YIELD')
    div_yield_pct = div_yield_val * 100 if div_yield_val > 0 else 0.0
    
    # Chỉ số BCTC nâng cao (từ Vnstock KBS - nguồn duy nhất có Net Margin & D/E)
    bctc = _kbs_get_bctc_ratios(symbol)
    net_profit_margin = bctc['net_margin']       # % hoặc None
    debt_on_equity = bctc['debt_to_equity']       # lần hoặc None
    gross_margin = bctc['gross_margin']           # % hoặc None

    price_vnd = current_price * 1000
    eps = price_vnd / pe if pe > 0 else 0.0
    roe = (eps / bvps) * 100 if bvps > 0 else 0.0

    # Ngành nghề, Nhóm ngành & Sàn giao dịch
    industry = "Đang cập nhật"
    floor = "N/A"
    try:
        url_stock = f"https://api-finfo.vndirect.com.vn/v4/stocks?q=code:{symbol}"
        r_stock = requests.get(url_stock, headers=VNDIRECT_HEADERS, timeout=VNDIRECT_TIMEOUT)
        data_stock = r_stock.json().get('data', [])
        if data_stock:
            industry = data_stock[0].get('companyName', industry)
            floor = data_stock[0].get('floor', floor)
            if industry.startswith("Công ty Cổ phần"):
                industry = industry.replace("Công ty Cổ phần", "CTCP").strip()
            elif industry.startswith("Công ty cổ phần"):
                industry = industry.replace("Công ty cổ phần", "CTCP").strip()
    except Exception:
        pass

    # Phân loại nhóm ngành (Sector)
    ind_lower = industry.lower()
    if any(kw in ind_lower for kw in ["ngân hàng", "chứng khoán", "bảo hiểm", "tài chính"]):
        sector = "FINANCE (Tài chính)"
    elif any(kw in ind_lower for kw in ["bất động sản", "địa ốc"]):
        sector = "REAL_ESTATE (Bất động sản)"
    else:
        sector = "GENERAL (Đa ngành)"

    # ═══════════════════════════════════════════════════════════════
    # 3. KIỂM TRA GATE & ĐÁNH GIÁ CÁC CHIẾN LƯỢC (CL1, CL2, CL3)
    # ═══════════════════════════════════════════════════════════════
    # Tính Thanh khoản TB 20 phiên (Tỷ VNĐ)
    # vol_ma20 (số cổ phiếu), current_price (nghìn đồng) -> (vol * price * 1000) / 1 tỷ = vol * price / 1_000_000
    trade_value_ty = (vol_ma20 * current_price) / 1000 
    
    gate_passed = True
    gate_reason = ""
    if trade_value_ty < 1.0:
        gate_passed = False
        gate_reason = f"Thanh khoản quá thấp ({trade_value_ty:.2f} Tỷ < 1 Tỷ/ngày)"
    elif bvps <= 0:
        gate_passed = False
        gate_reason = "Vốn chủ sở hữu âm (BVPS <= 0)"

    highest_20d = df_hist['high'].iloc[-21:-1].max() if len(df_hist) >= 21 else current_price
    lowest_120d = df_hist['low'].min()
    sma20 = df_hist['close'].rolling(20).mean().iloc[-1]
    std20 = df_hist['close'].rolling(20).std().iloc[-1]
    lower_bb = sma20 - 2 * std20
    # Tính ATR (Average True Range) để tính SL/TP động
    high_low = df_hist['high'] - df_hist['low']
    high_close = np.abs(df_hist['high'] - df_hist['close'].shift())
    low_close = np.abs(df_hist['low'] - df_hist['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(14).mean().iloc[-1]
    if pd.isna(atr):
        atr = current_price * 0.05
    
    # Tính SL/TP động cho CL1 (Đầu cơ Long/Short)
    sl_long = current_price - (2 * atr)
    tp_long = current_price + (3 * atr)
    sl_short = current_price + (2 * atr)
    tp_short = current_price - (3 * atr)

    # Tính SL/TP cho CL2
    sl_cl2 = current_price - (2 * atr)
    tp_cl2 = current_price + (3 * atr)

    # Tính SL/TP cho CL3 (Dài hạn)
    sl_cl3 = min(lowest_120d, lower_bb) * 0.95
    tp_cl3 = current_price * 1.30

    if not gate_passed:
        sig_cl1 = sig_cl2 = sig_cl3 = "KHÔNG KHUYẾN NGHỊ"
        final_decision = f"🚫 KHÔNG KHUYẾN NGHỊ (Lỗi Gate: {gate_reason})"
        margin_status = "❌ Cấm dùng"
        confidence = 0
    else:
        # --- CL1: Kỹ thuật ---
        sig_cl1 = "THEO DÕI"
        if ema20 > ema50 and 50 < rsi_14 < 70 and current_vol > 1.2 * vol_ma20:
            sig_cl1 = "MUA"
        elif rsi_14 >= 70:
            sig_cl1 = "GIẢM TỶ TRỌNG"
        elif current_price < ema20:
            sig_cl1 = "BÁN"

        # --- CL2: Cơ bản & Dòng tiền ---
        sig_cl2 = "THEO DÕI"
        if eps > 0 and roe > 10:
            if current_price > highest_20d and current_vol >= 1.5 * vol_ma20:
                sig_cl2 = "MUA"
            elif current_price < ema50:
                sig_cl2 = "BÁN"
            elif current_price >= highest_20d * 0.95:
                sig_cl2 = "GIẢM TỶ TRỌNG"
            else:
                sig_cl2 = "THEO DÕI"
        else:
            sig_cl2 = "THEO DÕI"

        # --- CL3: Giá trị & Cổ tức ---
        sig_cl3 = "THEO DÕI"
        is_near_support = current_price <= lower_bb * 1.05 or current_price <= lowest_120d * 1.05
        is_reversal = current_price > latest['open']
        
        if div_yield_pct >= 3.0 and 0 < pe < 15:
            if is_near_support and is_reversal:
                sig_cl3 = "MUA"
        
        # Tính tỷ trọng Margin dựa trên dữ liệu thật
        # - Xu hướng phải TĂNG (Giá > EMA20 > EMA50)
        # - RSI không được quá mua (< 65)
        # - D/E phải an toàn (< 1.0)
        margin_weight = 0
        if current_price > ema20 > ema50:
            margin_weight += 30
        if 40 < rsi_14 < 65:
            margin_weight += 20
        if debt_on_equity is not None and debt_on_equity < 1.0:
            margin_weight += 20
        elif debt_on_equity is None:
            margin_weight += 0
            
        if sig_cl1 == "BÁN" or rsi_14 > 70:
            margin_weight = 0
            
        if margin_weight == 0:
            margin_status = "❌ 0% (Rủi ro cao/Xu hướng giảm)"
        elif margin_weight <= 30:
            margin_status = f"⚠️ Tối đa {margin_weight}% (Thận trọng)"
        else:
            margin_status = f"✅ Tối đa {margin_weight}% (An toàn)"

        # Tính độ tự tin (Confidence Score)
        # Cơ sở: AI Score / 10 + Các yếu tố xác nhận
        confidence_base = 50 # Mặc định 50%
        
        # --- TỔNG HỢP KHUYẾN NGHỊ THEO BẢNG CHUẨN ---
        all_sigs = {'CL1': sig_cl1, 'CL2': sig_cl2, 'CL3': sig_cl3}
        main_sig = all_sigs.get(main_strategy, sig_cl1)
        sub_sigs = [v for k, v in all_sigs.items() if k != main_strategy]
        
        if main_sig == "MUA":
            if "MUA" in sub_sigs:
                final_decision = "🔥 MUA MẠNH"
                confidence = confidence_base + 35
            else:
                final_decision = "🟢 MUA"
                confidence = confidence_base + 20
        elif main_sig == "BÁN":
            final_decision = "🔴 BÁN (Chạm Stop Loss/Gãy nền)"
            confidence = confidence_base + 30
        elif main_sig == "GIẢM TỶ TRỌNG":
            final_decision = "⚠️ GIẢM TỶ TRỌNG"
            confidence = confidence_base + 10
        else:
            final_decision = "👀 THEO DÕI / GIỮ"
            confidence = confidence_base
            
    # Đổi chiến lược chính thành tên hiển thị
    strategy_names = {
        "CL1": "Ngắn hạn (< 3 Tháng)",
        "CL2": "Trung hạn (3-12 Tháng)",
        "CL3": "Dài hạn (> 12 Tháng)"
    }
    main_st_name = strategy_names.get(main_strategy, "Ngắn hạn (< 3 Tháng)")

    # ═══════════════════════════════════════════════════════════════
    # 4. TÍNH ĐIỂM AI SMARTCORE
    # ═══════════════════════════════════════════════════════════════
    score = 0.0
    details = []

    if 0 < pe <= 10:
        score += 2.0; details.append("P/E rất rẻ (+2đ)")
    elif 10 < pe <= 15:
        score += 1.0; details.append("P/E hợp lý (+1đ)")

    if roe > 20:
        score += 3.0; details.append("ROE xuất sắc (+3đ)")
    elif roe > 15:
        score += 2.0; details.append("ROE tốt (+2đ)")
    elif roe > 10:
        score += 1.0; details.append("ROE khá (+1đ)")

    if current_price > ema20 > ema50:
        score += 1.5; details.append("Trend tăng khỏe (+1.5đ)")
    elif current_price > ema20:
        score += 0.5; details.append("Trend ngắn hạn ổn (+0.5đ)")

    if vol_ratio > 150:
        score += 1.5; details.append("Dòng tiền rất mạnh (+1.5đ)")
    elif vol_ratio > 120:
        score += 0.5; details.append("Dòng tiền khá (+0.5đ)")
        
    # Chấm điểm Sức khoẻ BCTC (Tối đa 2đ)
    if net_profit_margin is not None:
        if net_profit_margin > 15:
            score += 1.0; details.append("Biên lợi nhuận cao (+1đ)")
        elif net_profit_margin > 5:
            score += 0.5; details.append("Biên lợi nhuận ổn (+0.5đ)")
        
    if debt_on_equity is not None:
        if 0 <= debt_on_equity < 1.0:
            score += 1.0; details.append("Tài chính an toàn (+1đ)")
        elif debt_on_equity < 2.0:
            score += 0.5; details.append("Nợ vay kiểm soát được (+0.5đ)")

    score = min(score, 10.0)
    
    # Cộng thêm điểm AI vào độ tự tin (Mỗi 1 điểm = 1.5%)
    confidence = min(99, confidence + int(score * 1.5))
    
    if score >= 8: ai_rank = "⭐ HẠNG A (Xuất Sắc)"
    elif score >= 6: ai_rank = "⭐ HẠNG B (Khá Tốt)"
    elif score >= 4: ai_rank = "⚠️ HẠNG C (Trung Bình)"
    else: ai_rank = "❌ HẠNG D (Yếu)"

    # ——————————————————————————————————————
    # 5. RENDER TEMPLATE THEO CHIẾN LƯỢC CHÍNH
    # ——————————————————————————————————————
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sign = "+" if price_change_pct > 0 else ""

    msg = f"""📊 **{symbol} ({floor}) - {industry}**
🕒 Cập nhật: {now_str}
🏢 Nhóm ngành: {sector}

🎯 **KHUYẾN NGHỊ CUỐI CÙNG: {final_decision}**
*(Độ tự tin: {confidence}% | Theo chiến lược {main_st_name})*
"""

    if main_strategy == "CL1":
        msg += f"""
🔥 **GÓC ĐẦU CƠ - TRADING NGẮN HẠN (CL1)**
• Tín hiệu: {sig_cl1}
• Giá hiện tại: {current_price:,.1f} ({sign}{price_change_pct:.2f}%)
• Khối lượng: {current_vol:,.0f} (~{vol_ratio:.1f}% BQ 20D)
• Chỉ báo RSI(14): {rsi_14:.2f}
• Đòn bẩy (Margin): {margin_status}
📈 **Vị thế Mua (Long):**
  🛡 Hỗ trợ (SL): {sl_long:,.2f} | 🎯 Mục tiêu (TP): {tp_long:,.2f}
📉 **Vị thế Bán khống (Short):**
  🛡 Hỗ trợ (SL): {sl_short:,.2f} | 🎯 Mục tiêu (TP): {tp_short:,.2f}
"""
    elif main_strategy == "CL2":
        msg += f"""
📈 **GÓC ĐẦU TƯ - TĂNG TRƯỞNG & DÒNG TIỀN (CL2)**
• Tín hiệu: {sig_cl2}
• Giá hiện tại: {current_price:,.1f} ({sign}{price_change_pct:.2f}%)
• Khối lượng: {current_vol:,.0f} (~{vol_ratio:.1f}% BQ 20D)
• Điểm bứt phá (Pivot 20D): {highest_20d:,.1f}
• Đòn bẩy (Margin): {margin_status}
🛡 Hỗ trợ (SL): {sl_cl2:,.2f} | 🎯 Mục tiêu (TP): {tp_cl2:,.2f}
"""
    elif main_strategy == "CL3":
        msg += f"""
💎 **GÓC ĐẦU TƯ - GIÁ TRỊ & CỔ TỨC (CL3)**
• Tín hiệu: {sig_cl3}
• Giá hiện tại: {current_price:,.1f} ({sign}{price_change_pct:.2f}%)
• Vùng đáy an toàn (Lower BB/120D): {min(lowest_120d, lower_bb):,.1f}
• Lãi suất Cổ tức: {div_yield_pct:.2f}% (Chuẩn >= 3%)
• Định giá P/E: {pe:.2f} (Chuẩn < 15)
🛡 Hỗ trợ cắt lỗ (SL): {sl_cl3:,.2f} | 🎯 Mục tiêu dài hạn (TP): {tp_cl3:,.2f}
"""

    msg += f"""
🤖 **AI SMARTCORE ĐÁNH GIÁ CHUNG**
• Điểm AI: {score}/10 Điểm ({ai_rank})
• Phân tích: {', '.join(details) if details else 'Chưa đạt tiêu chí nào'}
• Vốn hóa: {market_cap:,.0f} Tỷ | EPS: {eps:,.0f} VNĐ
• P/E: {pe:.2f} | P/B: {pb:.2f} | ROE: {roe:.2f}%
• Biên lợi nhuận (Net Margin): {f'{net_profit_margin:.1f}%' if net_profit_margin is not None else 'N/A'}
• Tỷ lệ Nợ/Vốn chủ (D/E): {f'{debt_on_equity:.2f} lần' if debt_on_equity is not None else 'N/A'}"""

    return msg

if __name__ == "__main__":
    print(analyze_stock("FPT", "CL2"))
