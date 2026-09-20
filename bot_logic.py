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


def analyze_stock(symbol: str) -> str:
    """
    Hàm phân tích mã cổ phiếu và sinh ra chuỗi markdown cho Telegram.
    Toàn bộ dữ liệu lấy từ VNDirect API (nhanh, chính xác, không bị chặn).
    """
    symbol = symbol.upper()

    # ═══════════════════════════════════════════════════════════════
    # 1. LẤY DỮ LIỆU LỊCH SỬ GIÁ
    # ═══════════════════════════════════════════════════════════════
    df_hist = _vnd_get_history(symbol, days=120)
    
    if df_hist.empty or len(df_hist) < 3:
        return f"❌ Không thể lấy đủ dữ liệu lịch sử giá cho mã {symbol}."

    # Tính toán các chỉ báo Kỹ thuật
    df_hist['EMA20'] = df_hist['close'].ewm(span=20, adjust=False).mean()
    df_hist['EMA50'] = df_hist['close'].ewm(span=50, adjust=False).mean()
    df_hist['RSI14'] = calculate_rsi(df_hist, window=14)
    df_hist['Vol_MA20'] = df_hist['volume'].rolling(window=20).mean()

    latest = df_hist.iloc[-1]
    prev = df_hist.iloc[-2]

    current_price = latest['close']       # Đơn vị: nghìn đồng (VD: 61.2)
    price_change_pct = ((current_price - prev['close']) / prev['close']) * 100
    current_vol = latest['volume']
    vol_ma20 = latest['Vol_MA20']
    vol_ratio = (current_vol / vol_ma20) * 100 if vol_ma20 > 0 else 0
    rsi_14 = latest['RSI14']
    ema20 = latest['EMA20']
    ema50 = latest['EMA50']

    # ═══════════════════════════════════════════════════════════════
    # 2. LẤY DỮ LIỆU TÀI CHÍNH TỪ VNDIRECT API (NHANH & CHUẨN)
    # ═══════════════════════════════════════════════════════════════
    pe = _vnd_get_ratio(symbol, 'PRICE_TO_EARNINGS')
    pb = _vnd_get_ratio(symbol, 'PRICE_TO_BOOK')
    market_cap_raw = _vnd_get_ratio(symbol, 'MARKETCAP')        # VNĐ nguyên
    market_cap = market_cap_raw / 1e9 if market_cap_raw > 1e6 else market_cap_raw  # → Tỷ VNĐ
    bvps_raw = _vnd_get_ratio(symbol, 'BVPS_CR')                # VNĐ nguyên
    bvps = bvps_raw                                               # Giữ nguyên VNĐ
    outstanding_shares = _vnd_get_ratio(symbol, 'OUTSTANDING_SHARES')  # Số CP lưu hành

    # Tính EPS = Giá (VNĐ) / P/E
    price_vnd = current_price * 1000  # Chuyển từ nghìn đồng → VNĐ
    eps = price_vnd / pe if pe > 0 else 0.0

    # Tính ROE = EPS / BVPS × 100 (%)
    roe = (eps / bvps) * 100 if bvps > 0 else 0.0

    # Ngành nghề - Lấy từ VCI overview (có cache, nhanh)
    industry = "Chưa phân loại"
    try:
        from vnstock.api.company import Company
        df_ov = Company(symbol=symbol, source='KBS').overview()
        if df_ov is not None and not df_ov.empty:
            if 'company_type' in df_ov.columns:
                industry = str(df_ov['company_type'].iloc[0])
    except Exception:
        pass

    # ═══════════════════════════════════════════════════════════════
    # 3. ĐÁNH GIÁ TÍN HIỆU KỸ THUẬT (CL1)
    # ═══════════════════════════════════════════════════════════════
    tech_signal = "⚠️ THEO DÕI"
    margin_status = "❌ Không nên dùng (Rủi ro)"
    if ema20 > ema50 and 50 < rsi_14 < 70 and current_vol > 1.2 * vol_ma20:
        tech_signal = "🟢 MUA MẠNH"
        margin_status = "✅ Có thể dùng mức thấp"
    elif rsi_14 > 70 or current_price < ema20:
        tech_signal = "🔴 GIẢM TỶ TRỌNG / BÁN"

    sl = current_price * 0.93
    tp = current_price * 1.10

    # ═══════════════════════════════════════════════════════════════
    # 4. TÍNH ĐIỂM AI SMARTCORE
    # ═══════════════════════════════════════════════════════════════
    score = 0.0
    details = []

    # 4.1 Định giá (P/E) - Max 2đ
    if 0 < pe <= 10:
        score += 2.0
        details.append("P/E rất rẻ (+2đ)")
    elif 10 < pe <= 15:
        score += 1.0
        details.append("P/E hợp lý (+1đ)")

    # 4.2 Hiệu quả kinh doanh (ROE) - Max 3đ
    if roe > 20:
        score += 3.0
        details.append("ROE xuất sắc (+3đ)")
    elif roe > 15:
        score += 2.0
        details.append("ROE tốt (+2đ)")
    elif roe > 10:
        score += 1.0
        details.append("ROE khá (+1đ)")

    # 4.3 Xu hướng kỹ thuật (Trend) - Max 2đ
    if current_price > ema20 > ema50:
        score += 2.0
        details.append("Trend tăng khỏe (+2đ)")
    elif current_price > ema20:
        score += 1.0
        details.append("Trend ngắn hạn ổn (+1đ)")

    # 4.4 Dòng tiền (Khối lượng) - Max 3đ
    if vol_ratio > 150:
        score += 3.0
        details.append("Dòng tiền vào rất mạnh (+3đ)")
    elif vol_ratio > 120:
        score += 1.5
        details.append("Dòng tiền vào khá (+1.5đ)")

    score = min(score, 10.0)

    if score >= 8:
        ai_rank = "⭐ HẠNG A (Xuất Sắc) ➡ 🟢 MUA MẠNH"
    elif score >= 6:
        ai_rank = "⭐ HẠNG B (Khá Tốt) ➡ 🟢 MUA / NẮM GIỮ"
    elif score >= 4:
        ai_rank = "⭐ HẠNG C (Trung Bình) ➡ ⚠️ THEO DÕI"
    else:
        ai_rank = "⭐ HẠNG D (Yếu) ➡ 🔴 BÁN / ĐỨNG NGOÀI"

    # ═══════════════════════════════════════════════════════════════
    # 5. RENDER TEMPLATE
    # ═══════════════════════════════════════════════════════════════
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    sign = "+" if price_change_pct > 0 else ""

    msg = f"""📊 **{symbol} - {industry}**
🕒 Cập nhật: {now_str}

🔥 **[GÓC ĐẦU CƠ - TRADING THEO DÒNG TIỀN]**
• Tín hiệu Kỹ thuật (CL1): {tech_signal}
• Đòn bẩy (Margin): {margin_status}
• Giá hiện tại: {current_price:,.1f} ({sign}{price_change_pct:.2f}%)
• Khối lượng: {current_vol:,.0f} (~{vol_ratio:.1f}% BQ 20 phiên)
• Chỉ số RSI(14): {rsi_14:.2f}
🎯 Chốt lời (TP): {tp:,.2f} | Cắt lỗ (SL): {sl:,.2f}

💎 **[GÓC ĐẦU TƯ - TÍCH SẢN GIÁ TRỊ]**
• AI SmartCore: {score}/10 Điểm
🎯 Phân loại: {ai_rank}
🔍 Chi tiết: {', '.join(details) if details else 'Chưa đạt tiêu chí nào'}
🏢 Nhóm ngành: {industry}
💰 Vốn hóa: {market_cap:,.0f} Tỷ
📈 EPS: {eps:,.0f} VNĐ | P/E: {pe:.2f}
📚 PVPS (BVPS): {bvps:,.0f} VNĐ | P/B: {pb:.2f} | ROE: {roe:.2f}%"""

    return msg


if __name__ == "__main__":
    print(analyze_stock("VNM"))
