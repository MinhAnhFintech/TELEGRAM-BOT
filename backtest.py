import pandas as pd
import numpy as np
import requests
import argparse
import sys
from datetime import datetime

# Khắc phục lỗi in Unicode trên Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ═══════════════════════════════════════════════════════════════
# 1. HÀM LẤY DỮ LIỆU LỊCH SỬ TỪ VNDIRECT
# ═══════════════════════════════════════════════════════════════
def get_historical_data(symbol: str, days: int = 1000) -> pd.DataFrame:
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        url = f"https://api-finfo.vndirect.com.vn/v4/stock_prices?sort=date&q=code:{symbol}&size={days}&page=1"
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json().get('data', [])
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
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
        print(f"Lỗi: {e}")
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════
# 2. TÍNH TOÁN CÁC CHỈ BÁO KỸ THUẬT
# ═══════════════════════════════════════════════════════════════
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['SMA50'] = df['close'].rolling(50).mean()
    df['SMA200'] = df['close'].rolling(200).mean()
    df['Vol_MA20'] = df['volume'].rolling(20).mean()
    
    # ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(14).mean()
    
    # MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # Kéo MACD_Hist của phiên trước (để so sánh điểm cắt)
    df['Prev_MACD_Hist'] = df['MACD_Hist'].shift(1)
    
    return df

# ═══════════════════════════════════════════════════════════════
# 3. ENGINE BACKTEST
# ═══════════════════════════════════════════════════════════════
def run_backtest(df: pd.DataFrame, strategy: str = "CL1", initial_capital: float = 100_000_000):
    trades = []
    capital = initial_capital
    position = 0
    in_trade = False
    
    entry_price = 0
    entry_date = None
    sl_price = 0
    tp_price = 0
    
    # Phí & Thuế (Nguyên tắc Backtest Mục 13)
    FEE_BUY = 0.0015  # 0.15% phí mua
    FEE_SELL = 0.0015 # 0.15% phí bán
    TAX_SELL = 0.0010 # 0.1% thuế bán
    
    # Trailing stop
    highest_price_since_entry = 0
    
    # Bắt đầu duyệt từ ngày 200 (đợi đủ data cho SMA200)
    for i in range(200, len(df) - 1):
        today = df.iloc[i]
        tomorrow = df.iloc[i+1] # Giá mở cửa hôm sau để khớp lệnh thực tế
        
        # Nếu đang giữ cổ phiếu
        if in_trade:
            sell_price = 0
            sell_reason = ""
            
            # Cập nhật trailing đỉnh
            if today['high'] > highest_price_since_entry:
                highest_price_since_entry = today['high']
            
            # 1. Kiểm tra Trailing Stop Loss & Max Loss
            loss_pct = (today['low'] - entry_price) / entry_price
            trailing_drop = (highest_price_since_entry - today['low']) / highest_price_since_entry
            
            if strategy == "CL1" and trailing_drop >= 0.10: # Trailing Stop 10% (Alg 2.1)
                sell_price = today['low'] if today['open'] > today['low'] else today['open']
                sell_reason = "Trailing Stop 10%"
            elif strategy == "CL2" and loss_pct <= -0.075: # Cut loss 7.5% (Alg 3.2.2)
                sell_price = today['low'] if today['open'] > today['low'] else today['open']
                sell_reason = "Cut Loss 7.5%"
            elif strategy == "CL2" and trailing_drop >= 0.10: # Trailing Stop 10% (Alg 3.1.1)
                sell_price = today['low'] if today['open'] > today['low'] else today['open']
                sell_reason = "Trailing Stop 10%"
            elif strategy == "CL3" and loss_pct <= -0.20: # Max Loss Limit = 20% (Alg 4.1)
                sell_price = today['low'] if today['open'] > today['low'] else today['open']
                sell_reason = "Max Loss 20%"
            elif today['low'] <= sl_price:
                sell_price = sl_price
                sell_reason = "Hit SL ATR"
            elif today['high'] >= tp_price:
                sell_price = tp_price
                sell_reason = "Hit TP ATR"
            else:
                # 2. Kiểm tra tín hiệu BÁN kỹ thuật
                sell_signal = False
                if strategy == "CL1":
                    if today['close'] < today['SMA50'] or (today['MACD_Hist'] < 0 and today['Prev_MACD_Hist'] >= 0):
                        sell_signal = True
                elif strategy == "CL2":
                    if today['close'] < today['SMA50']: # Rơi xuống dưới MA50 (Alg 3.1.1)
                        sell_signal = True
                elif strategy == "CL3":
                    prev_sma50 = df.iloc[i-1]['SMA50']
                    prev_sma200 = df.iloc[i-1]['SMA200']
                    if today['close'] < today['SMA200'] or (today['SMA50'] < today['SMA200'] and prev_sma50 >= prev_sma200):
                        sell_signal = True
                
                if sell_signal:
                    sell_price = tomorrow['open'] # Bán ở giá mở cửa ngày hôm sau
                    sell_reason = "Tech Exit"
            
            # Thực thi BÁN
            if sell_price > 0:
                gross_return = (sell_price - entry_price) / entry_price
                net_return = gross_return - FEE_BUY - FEE_SELL - TAX_SELL
                profit = capital * net_return
                capital += profit
                
                trades.append({
                    'Entry_Date': entry_date,
                    'Exit_Date': tomorrow['date'] if sell_reason == "Tech Exit" else today['date'],
                    'Entry_Price': entry_price,
                    'Exit_Price': sell_price,
                    'Return_%': net_return * 100,
                    'Profit': profit,
                    'Reason': sell_reason
                })
                in_trade = False
                highest_price_since_entry = 0
                
        # Nếu chưa giữ cổ phiếu -> Tìm điểm MUA
        if not in_trade:
            buy_signal = False
            if strategy == "CL1":
                # Vol ratio > 1.5, Giá > SMA50, MACD chớm dương
                if today['close'] > today['SMA50'] and today['MACD_Hist'] > 0 and today['Prev_MACD_Hist'] <= 0 and today['volume'] > 1.5 * today['Vol_MA20']:
                    buy_signal = True
            elif strategy == "CL2":
                highest_20d = df['high'].iloc[max(0, i-20):i].max()
                # CL2 V3: Nằm TRÊN MA50 và MACD khả quan
                if today['close'] > highest_20d and today['volume'] >= 1.5 * today['Vol_MA20'] and today['close'] > today['SMA50'] and today['MACD_Hist'] > 0:
                    buy_signal = True
            elif strategy == "CL3":
                lowest_120d = df['low'].iloc[max(0, i-120):i].min()
                prev_sma50 = df.iloc[i-1]['SMA50']
                prev_sma200 = df.iloc[i-1]['SMA200']
                if (today['SMA50'] > today['SMA200'] and prev_sma50 <= prev_sma200) or \
                   (today['MACD_Hist'] > 0 and today['Prev_MACD_Hist'] <= 0 and today['close'] <= lowest_120d * 1.10):
                    buy_signal = True
            
            if buy_signal:
                in_trade = True
                entry_date = tomorrow['date']
                entry_price = tomorrow['open'] # Khớp ở giá mở cửa ngày hôm sau (Nguyên tắc Backtest)
                highest_price_since_entry = entry_price
                
                # Setup SL / TP dựa trên ATR ngày hôm nay
                atr = today['ATR'] if pd.notna(today['ATR']) else (today['close'] * 0.05)
                sl_price = today['close'] - (2 * atr)
                tp_price = today['close'] + (3 * atr)
                
    # --- ĐÁNH GIÁ HIỆU QUẢ ---
    df_trades = pd.DataFrame(trades)
    
    print("\n" + "="*50)
    print(f"🔥 KẾT QUẢ BACKTEST CHIẾN LƯỢC {strategy} 🔥")
    print("="*50)
    
    if df_trades.empty:
        print("Không có lệnh giao dịch nào được thực thi.")
        return

    total_trades = len(df_trades)
    win_trades = len(df_trades[df_trades['Return_%'] > 0])
    loss_trades = total_trades - win_trades
    win_rate = win_trades / total_trades * 100
    
    total_profit = df_trades['Profit'].sum()
    final_capital = initial_capital + total_profit
    roi = (final_capital - initial_capital) / initial_capital * 100
    
    # Buy & Hold return
    first_price = df.iloc[200]['open']
    last_price = df.iloc[-1]['close']
    bnh_return = (last_price - first_price) / first_price * 100
    
    # Max Drawdown
    cumulative = initial_capital + df_trades['Profit'].cumsum()
    running_max = cumulative.cummax()
    drawdowns = (cumulative - running_max) / running_max * 100
    max_dd = drawdowns.min() if not drawdowns.empty else 0
    
    print(f"• Số lượng lệnh (Total Trades): {total_trades} lệnh")
    print(f"• Tỷ lệ thắng (Win Rate):       {win_rate:.2f}% ({win_trades} Thắng / {loss_trades} Thua)")
    print(f"• Lãi trung bình lệnh thắng:    {df_trades[df_trades['Return_%'] > 0]['Return_%'].mean():.2f}%")
    print(f"• Lỗ trung bình lệnh thua:      {df_trades[df_trades['Return_%'] < 0]['Return_%'].mean():.2f}%")
    print("-" * 50)
    print(f"• Lợi nhuận gộp (Net PNL):      {total_profit:,.0f} VNĐ")
    print(f"• Tỷ suất sinh lời (ROI):       {roi:.2f}%")
    print(f"• Drawdown lớn nhất (Max DD):   {max_dd:.2f}%")
    print(f"• Buy & Hold Cổ phiếu (B&H):    {bnh_return:.2f}%")
    print("="*50)
    print("\nLỊCH SỬ 5 LỆNH GẦN NHẤT:")
    print(df_trades.tail(5)[['Entry_Date', 'Exit_Date', 'Return_%', 'Reason']].to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Backtest Chiến Lược AI SmartCore')
    parser.add_argument('--symbol', type=str, default='VNM', help='Mã cổ phiếu (VD: FPT, VNM, HPG)')
    parser.add_argument('--strategy', type=str, default='CL1', help='Chiến lược (CL1, CL2, CL3)')
    parser.add_argument('--days', type=int, default=1000, help='Số ngày lịch sử (VD: 1000 = ~4 năm)')
    args = parser.parse_args()

    print(f"⏳ Đang tải dữ liệu {args.symbol} ({args.days} ngày)...")
    df = get_historical_data(args.symbol, days=args.days)
    if df.empty:
        print("Lỗi: Không lấy được dữ liệu.")
    else:
        df = calculate_indicators(df)
        run_backtest(df, strategy=args.strategy)