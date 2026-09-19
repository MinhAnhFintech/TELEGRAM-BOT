import pandas as pd
import numpy as np
import qlib

def calculate_ema(series, periods):
    """Tính Exponential Moving Average"""
    return series.ewm(span=periods, adjust=False).mean()

def calculate_rsi(series, periods=14):
    """Tính Relative Strength Index (RSI) chuẩn theo J. Welles Wilder"""
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/periods, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/periods, adjust=False).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi



def check_signal(df):
    """
    Phân tích và trả về tín hiệu: BUY, SELL, hoặc HOLD.
    Dựa trên Chiến lược 1 (Phân tích Kỹ thuật).
    """
    if df is None or len(df) < 60:
        return "NOT_ENOUGH_DATA", 0, 0
        
    df = df.copy()
    
    # Tính các chỉ báo kỹ thuật
    df['EMA_20'] = calculate_ema(df['close'], 20)
    df['EMA_50'] = calculate_ema(df['close'], 50)
    df['RSI_14'] = calculate_rsi(df['close'], 14)
    
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    signal = "HOLD"
    
    # --- LOGIC MUA (BUY) ---
    # Điều kiện 1: EMA 20 cắt lên EMA 50 (Golden Cross) VÀ RSI > 50
    golden_cross = (prev['EMA_20'] <= prev['EMA_50']) and (last['EMA_20'] > last['EMA_50'])
    
    # Điều kiện 2: Xu hướng đang tăng (EMA20 > EMA50) và RSI vừa vượt lên 50 (Momentum tốt)
    rsi_breakout = (last['EMA_20'] > last['EMA_50']) and (prev['RSI_14'] <= 50) and (last['RSI_14'] > 50)
    
    if golden_cross or rsi_breakout:
        # Check thêm điều kiện volume bùng nổ (tùy chọn) - nhưng ta giữ logic đơn giản trước
        signal = "BUY"
        
    # --- LOGIC BÁN (SELL) ---
    # Điều kiện 1: Giá thủng đường hỗ trợ (EMA 50)
    price_break_support = (prev['close'] >= prev['EMA_50']) and (last['close'] < last['EMA_50'])
    
    # Điều kiện 2: RSI đi vào vùng quá mua (>70) và quay đầu cắt xuống 70
    rsi_overbought_reversal = (prev['RSI_14'] >= 70) and (last['RSI_14'] < 70)
    
    if price_break_support or rsi_overbought_reversal:
        signal = "SELL"
        
    return signal, round(last['close'], 2), round(last['RSI_14'], 2)

