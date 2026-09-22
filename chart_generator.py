"""
Module vẽ biểu đồ Trading gửi qua Telegram.
Mỗi chiến lược CL1/CL2/CL3 có chart riêng, phù hợp với logic đầu tư.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
from datetime import datetime
import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

CHART_DIR = os.path.join(os.path.dirname(__file__), 'data', 'output')
os.makedirs(CHART_DIR, exist_ok=True)


def _prepare_data(symbol: str, days: int = 120) -> pd.DataFrame:
    """Lấy dữ liệu và tính toán các chỉ báo kỹ thuật."""
    from bot_logic import _vnd_get_history
    df = _vnd_get_history(symbol, days=days)
    if df.empty or len(df) < 20:
        return pd.DataFrame()

    df['SMA50'] = df['close'].rolling(50).mean()
    df['SMA200'] = df['close'].rolling(200).mean()

    # Tính MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # RSI thủ công
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['Vol_MA20'] = df['volume'].rolling(window=20).mean()

    # Bollinger Bands (cho CL3)
    df['SMA20'] = df['close'].rolling(20).mean()
    df['BB_upper'] = df['SMA20'] + 2 * df['close'].rolling(20).std()
    df['BB_lower'] = df['SMA20'] - 2 * df['close'].rolling(20).std()

    # Tính ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    df['ATR'] = true_range.rolling(14).mean()

    return df


def _calc_fibonacci(df: pd.DataFrame) -> dict:
    """Tính các mức Fibonacci Retracement."""
    high = df['high'].max()
    low = df['low'].min()
    diff = high - low
    return {
        '0% (Day)': low,
        '23.6%': low + 0.236 * diff,
        '38.2%': low + 0.382 * diff,
        '50.0%': low + 0.5 * diff,
        '61.8%': low + 0.618 * diff,
        '100% (Dinh)': high,
    }


def _white_style():
    """Tạo style nền trắng chuyên nghiệp giống báo cáo tài chính."""
    mc = mpf.make_marketcolors(
        up='#26A69A', down='#EF5350',
        edge={'up': '#26A69A', 'down': '#EF5350'},
        wick={'up': '#26A69A', 'down': '#EF5350'},
        volume={'up': '#26A69A80', 'down': '#EF535080'},
    )
    return mpf.make_mpf_style(
        marketcolors=mc,
        figcolor='white',
        facecolor='white',
        gridcolor='#E0E0E0',
        gridstyle='--',
        gridaxis='both',
        edgecolor='#BDBDBD',
        rc={
            'axes.labelcolor': '#333333',
            'xtick.color': '#333333',
            'ytick.color': '#333333',
            'font.size': 9,
        }
    )


# ═══════════════════════════════════════════════════════════════
# CL1 - CHIẾN LƯỢC ĐẦU CƠ NGẮN HẠN (< 3 Tháng)
# Chia rõ 2 loại: LONG (Mua thường) và SHORT (Bán khống)
# ═══════════════════════════════════════════════════════════════

def _generate_cl1_chart(symbol: str, df: pd.DataFrame) -> str:
    """
    Biểu đồ CL1 - Đầu cơ ngắn hạn.
    - LONG (▲ xanh): EMA20 cắt lên EMA50 + RSI > 50 + Volume mạnh → Mua vào, chờ lên bán ra.
    - SHORT (▼ tím): EMA20 cắt xuống EMA50 hoặc RSI > 75 → Vay CP bán trước, chờ giảm mua lại.
    - SL/TP cụ thể trên chart.
    """
    df_plot = df.copy().set_index('date')
    df_plot.index = pd.DatetimeIndex(df_plot.index)

    latest = df.iloc[-1]
    current_price = latest['close']
    atr = latest['ATR'] if pd.notna(latest['ATR']) else (current_price * 0.05)
    
    sl_long = current_price - (2 * atr)
    tp_long = current_price + (3 * atr)
    sl_short = current_price + (2 * atr)
    tp_short = current_price - (3 * atr)

    # Tín hiệu LONG và SHORT
    long_marker = pd.Series(np.nan, index=df_plot.index)
    short_marker = pd.Series(np.nan, index=df_plot.index)

    for i in range(1, len(df)):
        sma50 = df['SMA50'].iloc[i]
        price = df['close'].iloc[i]
        macd_hist = df['MACD_Hist'].iloc[i]
        prev_macd_hist = df['MACD_Hist'].iloc[i-1]
        rsi = df['RSI'].iloc[i]
        vol = df['volume'].iloc[i]
        vol_ma = df['Vol_MA20'].iloc[i]
        idx = df_plot.index[i]

        # LONG: Cắt lên SMA50 hoặc MACD dương
        if price > sma50 and macd_hist > 0 and prev_macd_hist <= 0 and vol > 1.2 * vol_ma:
            long_marker.loc[idx] = df_plot['low'].iloc[i] * 0.98
        
        # SHORT: Thủng SMA50 hoặc MACD âm
        elif price < sma50 or (macd_hist < 0 and prev_macd_hist >= 0):
            short_marker.loc[idx] = df_plot['high'].iloc[i] * 1.02

    # Vẽ
    add_plots = [
        mpf.make_addplot(df_plot['SMA50'], color='#2980b9', width=1.2, linestyle='--', label='SMA50'),
        mpf.make_addplot(df_plot['RSI'], panel=2, color='#8e44ad', width=1),
        mpf.make_addplot([70]*len(df_plot), panel=2, color='#e74c3c', width=1, linestyle='--'),
        mpf.make_addplot([30]*len(df_plot), panel=2, color='#1abc9c', width=1, linestyle='--'),
    ]
    if long_marker.notna().any():
        add_plots.append(mpf.make_addplot(long_marker, type='scatter', markersize=120, marker='^', color='#00C853'))
    if short_marker.notna().any():
        add_plots.append(mpf.make_addplot(short_marker, type='scatter', markersize=120, marker='v', color='#AA00FF'))

    # Đường SL/TP
    hlines_dict = dict(
        hlines=[sl_long, tp_long, sl_short, tp_short],
        colors=['#EF5350', '#26A69A', '#FF6D00', '#2979FF'],
        linestyle=['--', '--', '-.', '-.'],
        linewidths=[1, 1, 1, 1],
    )

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    fig, axes = mpf.plot(
        df_plot, type='candle', style=_white_style(),
        volume=True, addplot=add_plots, hlines=hlines_dict,
        figsize=(14, 9), returnfig=True, tight_layout=True,
        title='',
    )

    ax = axes[0]
    ax.set_title(f'{symbol} - CL1: DAU CO NGAN HAN (Long & Short)\n'
                 f'Cap nhat: {now_str} | EMA20 (cam) + EMA50 (xanh)',
                 fontsize=13, fontweight='bold', color='#333', pad=15)

    # Nhãn SL/TP cụ thể
    ax.annotate(f'SL Long: {sl_long:,.1f}', xy=(1.01, sl_long), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#EF5350', fontweight='bold', va='center')
    ax.annotate(f'TP Long: {tp_long:,.1f}', xy=(1.01, tp_long), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#26A69A', fontweight='bold', va='center')
    ax.annotate(f'SL Short: {sl_short:,.1f}', xy=(1.01, sl_short), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#FF6D00', fontweight='bold', va='center')
    ax.annotate(f'TP Short: {tp_short:,.1f}', xy=(1.01, tp_short), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#2979FF', fontweight='bold', va='center')

    # Legend
    ax.plot([], [], color='#FF6F00', lw=2, label='EMA20')
    ax.plot([], [], color='#1565C0', lw=2, label='EMA50')
    ax.scatter([], [], color='#00C853', marker='^', s=80, label='LONG (Mua vao)')
    ax.scatter([], [], color='#AA00FF', marker='v', s=80, label='SHORT (Ban khong)')
    ax.plot([], [], '--', color='#EF5350', lw=1, label=f'SL Long: {sl_long:,.1f}')
    ax.plot([], [], '--', color='#26A69A', lw=1, label=f'TP Long: {tp_long:,.1f}')
    ax.plot([], [], '-.', color='#FF6D00', lw=1, label=f'SL Short: {sl_short:,.1f}')
    ax.plot([], [], '-.', color='#2979FF', lw=1, label=f'TP Short: {tp_short:,.1f}')
    ax.legend(loc='upper left', fontsize=7.5, facecolor='white', edgecolor='#CCCCCC', framealpha=0.95)

    # RSI panel labels
    ax_rsi = axes[4]  # RSI panel
    ax_rsi.axhline(y=70, color='#EF5350', linestyle='--', linewidth=0.7, alpha=0.7)
    ax_rsi.axhline(y=30, color='#26A69A', linestyle='--', linewidth=0.7, alpha=0.7)
    ax_rsi.axhline(y=50, color='#9E9E9E', linestyle=':', linewidth=0.5)
    ax_rsi.set_ylim(10, 90)

    filepath = os.path.join(CHART_DIR, f'{symbol}_CL1.png')
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return filepath


# ═══════════════════════════════════════════════════════════════
# CL2 - CHIẾN LƯỢC TĂNG TRƯỞNG & DÒNG TIỀN (3-12 Tháng)
# ═══════════════════════════════════════════════════════════════

def _generate_cl2_chart(symbol: str, df: pd.DataFrame) -> str:
    """
    Biểu đồ CL2 - Tăng trưởng.
    - Pivot 20D (đỉnh 20 phiên gần nhất): Điểm bứt phá.
    - EMA20/50: Xu hướng trung hạn.
    - Volume đột biến: Dòng tiền lớn xác nhận.
    - SL/TP cụ thể.
    """
    df_plot = df.copy().set_index('date')
    df_plot.index = pd.DatetimeIndex(df_plot.index)

    latest = df.iloc[-1]
    current_price = latest['close']
    atr = latest['ATR'] if pd.notna(latest['ATR']) else (current_price * 0.05)
    
    sl = current_price - (2 * atr)
    tp = current_price + (3 * atr)

    # Pivot 20D
    pivot_20d = df['high'].iloc[-21:-1].max() if len(df) >= 21 else current_price

    # Tín hiệu MUA breakout
    buy_marker = pd.Series(np.nan, index=df_plot.index)
    for i in range(21, len(df)):
        pivot = df['high'].iloc[max(0, i - 21):max(1, i - 1)].max() if i >= 21 else df['high'].iloc[:i].max() if i > 0 else df['high'].iloc[0]
        vol = df['volume'].iloc[i]
        vol_ma = df['Vol_MA20'].iloc[i]
        close = df['close'].iloc[i]
        sma50 = df['SMA50'].iloc[i]
        macd_hist = df['MACD_Hist'].iloc[i]
        
        if close > pivot and vol >= 1.5 * vol_ma and close > sma50 and macd_hist > 0:
            buy_marker.loc[df_plot.index[i]] = df_plot['low'].iloc[i] * 0.98

    add_plots = [
        mpf.make_addplot(df_plot['SMA50'], color='#2980b9', width=1.5, label='SMA50'),
        mpf.make_addplot(df_plot['SMA200'], color='#c0392b', width=1.5, label='SMA200'),
        mpf.make_addplot(df_plot['RSI'], panel=2, color='#8e44ad', width=1, ylabel='RSI'),
    ]
    if buy_marker.notna().any():
        add_plots.append(mpf.make_addplot(buy_marker, type='scatter', markersize=120, marker='^', color='#00C853'))

    fib = _calc_fibonacci(df)
    hlines_dict = dict(
        hlines=[sl, tp, pivot_20d] + list(fib.values()),
        colors=['#EF5350', '#26A69A', '#FF9800'] + ['#90A4AE'] * len(fib),
        linestyle=['--', '--', '-'] + ['--'] * len(fib),
        linewidths=[1.2, 1.2, 1.5] + [0.7] * len(fib),
    )

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    fig, axes = mpf.plot(
        df_plot, type='candle', style=_white_style(),
        volume=True, addplot=add_plots, hlines=hlines_dict,
        figsize=(14, 9), returnfig=True, tight_layout=True, title='',
    )

    ax = axes[0]
    ax.set_title(f'{symbol} - CL2: TANG TRUONG & DONG TIEN (3-12 Thang)\n'
                 f'Cap nhat: {now_str} | Pivot 20D + EMA + Fibonacci',
                 fontsize=13, fontweight='bold', color='#333', pad=15)

    ax.annotate(f'SL: {sl:,.1f}', xy=(1.01, sl), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#EF5350', fontweight='bold', va='center')
    ax.annotate(f'TP: {tp:,.1f}', xy=(1.01, tp), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#26A69A', fontweight='bold', va='center')
    ax.annotate(f'Pivot 20D: {pivot_20d:,.1f}', xy=(1.01, pivot_20d), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#FF9800', fontweight='bold', va='center')

    for label, price in fib.items():
        ax.annotate(f'{label}: {price:,.1f}', xy=(1.01, price), xycoords=('axes fraction', 'data'),
                    fontsize=7, color='#78909C', va='center')

    ax.plot([], [], color='#FF6F00', lw=2, label='EMA20')
    ax.plot([], [], color='#1565C0', lw=2, label='EMA50')
    ax.scatter([], [], color='#00C853', marker='^', s=80, label='MUA (Breakout Pivot)')
    ax.plot([], [], '-', color='#FF9800', lw=1.5, label=f'Pivot 20D: {pivot_20d:,.1f}')
    ax.plot([], [], '--', color='#EF5350', lw=1, label=f'SL: {sl:,.1f}')
    ax.plot([], [], '--', color='#26A69A', lw=1, label=f'TP: {tp:,.1f}')
    ax.legend(loc='upper left', fontsize=7.5, facecolor='white', edgecolor='#CCC', framealpha=0.95)

    ax_rsi = axes[4]
    ax_rsi.axhline(y=70, color='#EF5350', linestyle='--', linewidth=0.7)
    ax_rsi.axhline(y=30, color='#26A69A', linestyle='--', linewidth=0.7)
    ax_rsi.axhline(y=50, color='#9E9E9E', linestyle=':', linewidth=0.5)
    ax_rsi.set_ylim(10, 90)

    filepath = os.path.join(CHART_DIR, f'{symbol}_CL2.png')
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return filepath


# ═══════════════════════════════════════════════════════════════
# CL3 - CHIẾN LƯỢC GIÁ TRỊ & CỔ TỨC (> 12 Tháng)
# ═══════════════════════════════════════════════════════════════

def _generate_cl3_chart(symbol: str, df: pd.DataFrame) -> str:
    """
    Biểu đồ CL3 - Giá trị & Cổ tức.
    - Bollinger Bands: Tìm vùng đáy (giá chạm BB dưới).
    - Fibonacci: Vùng hỗ trợ dài hạn.
    - Nến đảo chiều: Xác nhận bắt đáy.
    - SL/TP cụ thể.
    """
    df_plot = df.copy().set_index('date')
    df_plot.index = pd.DatetimeIndex(df_plot.index)

    latest = df.iloc[-1]
    current_price = latest['close']
    lowest_120d = df['low'].min()
    lower_bb = latest['BB_lower']
    sl = min(lowest_120d, lower_bb) * 0.95
    tp = current_price * 1.30  # CL3 mục tiêu dài hạn

    # Tín hiệu bắt đáy / Dài hạn
    reversal_marker = pd.Series(np.nan, index=df_plot.index)
    for i in range(1, len(df)):
        close_i = df['close'].iloc[i]
        sma50 = df['SMA50'].iloc[i]
        sma200 = df['SMA200'].iloc[i]
        prev_sma50 = df['SMA50'].iloc[i-1]
        prev_sma200 = df['SMA200'].iloc[i-1]
        macd_hist = df['MACD_Hist'].iloc[i]
        prev_macd_hist = df['MACD_Hist'].iloc[i-1]
        
        cross_ma = (sma50 > sma200 and prev_sma50 <= prev_sma200)
        cross_macd_bottom = (macd_hist > 0 and prev_macd_hist <= 0 and close_i <= lowest_120d * 1.10)
        
        if cross_ma or cross_macd_bottom:
            reversal_marker.loc[df_plot.index[i]] = df_plot['low'].iloc[i] * 0.98

    add_plots = [
        mpf.make_addplot(df_plot['SMA50'], color='#2980b9', width=1.2, label='SMA50'),
        mpf.make_addplot(df_plot['SMA200'], color='#c0392b', width=1.2, label='SMA200'),
        mpf.make_addplot(df_plot['RSI'], panel=2, color='#8e44ad', width=1, ylabel='RSI'),
    ]
    if reversal_marker.notna().any():
        add_plots.append(mpf.make_addplot(reversal_marker, type='scatter', markersize=120, marker='^', color='#00C853'))

    fib = _calc_fibonacci(df)
    hlines_dict = dict(
        hlines=[sl, tp] + list(fib.values()),
        colors=['#EF5350', '#26A69A'] + ['#BCAAA4'] * len(fib),
        linestyle=['--', '--'] + ['--'] * len(fib),
        linewidths=[1.2, 1.2] + [0.7] * len(fib),
    )

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    fig, axes = mpf.plot(
        df_plot, type='candle', style=_white_style(),
        volume=True, addplot=add_plots, hlines=hlines_dict,
        figsize=(14, 9), returnfig=True, tight_layout=True, title='',
    )

    ax = axes[0]
    ax.set_title(f'{symbol} - CL3: GIA TRI & CO TUC (Dai han > 12 Thang)\n'
                 f'Cap nhat: {now_str} | Bollinger Bands + Fibonacci + Nen dao chieu',
                 fontsize=13, fontweight='bold', color='#333', pad=15)

    ax.annotate(f'SL: {sl:,.1f}', xy=(1.01, sl), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#EF5350', fontweight='bold', va='center')
    ax.annotate(f'TP: {tp:,.1f}', xy=(1.01, tp), xycoords=('axes fraction', 'data'),
                fontsize=8, color='#26A69A', fontweight='bold', va='center')

    for label, price in fib.items():
        ax.annotate(f'{label}: {price:,.1f}', xy=(1.01, price), xycoords=('axes fraction', 'data'),
                    fontsize=7, color='#8D6E63', va='center')

    ax.plot([], [], '--', color='#1565C0', lw=1, label='SMA20')
    ax.plot([], [], '--', color='#90A4AE', lw=0.8, label='Bollinger Bands')
    ax.scatter([], [], color='#00C853', marker='^', s=80, label='Nen dao chieu (Bat day)')
    ax.plot([], [], '--', color='#EF5350', lw=1, label=f'SL: {sl:,.1f}')
    ax.plot([], [], '--', color='#26A69A', lw=1, label=f'TP: {tp:,.1f}')
    ax.legend(loc='upper left', fontsize=7.5, facecolor='white', edgecolor='#CCC', framealpha=0.95)

    ax_rsi = axes[4]
    ax_rsi.axhline(y=70, color='#EF5350', linestyle='--', linewidth=0.7)
    ax_rsi.axhline(y=30, color='#26A69A', linestyle='--', linewidth=0.7)
    ax_rsi.axhline(y=50, color='#9E9E9E', linestyle=':', linewidth=0.5)
    ax_rsi.set_ylim(10, 90)

    filepath = os.path.join(CHART_DIR, f'{symbol}_CL3.png')
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return filepath


# ═══════════════════════════════════════════════════════════════
# HÀM CHÍNH - ROUTER THEO CHIẾN LƯỢC
# ═══════════════════════════════════════════════════════════════

def generate_trading_chart(symbol: str, strategy: str = "CL1") -> str:
    """
    Vẽ biểu đồ phù hợp theo chiến lược đầu tư.
    strategy: CL1, CL2, hoặc CL3
    Trả về đường dẫn file ảnh PNG.
    """
    symbol = symbol.upper()
    df = _prepare_data(symbol, days=120)
    if df.empty:
        return None

    if strategy == "CL1":
        return _generate_cl1_chart(symbol, df)
    elif strategy == "CL2":
        return _generate_cl2_chart(symbol, df)
    elif strategy == "CL3":
        return _generate_cl3_chart(symbol, df)
    else:
        return _generate_cl1_chart(symbol, df)


if __name__ == "__main__":
    for st in ["CL1", "CL2", "CL3"]:
        path = generate_trading_chart("FPT", strategy=st)
        print(f"{st}: {path}" if path else f"{st}: FAIL")
