import requests
import pandas as pd
import time
from datetime import datetime

def get_historical_data(ticker, days=365):
    """
    Lấy dữ liệu lịch sử giá của một mã cổ phiếu từ DNSE (Entrade) API.
    """
    end_time = int(time.time())
    start_time = end_time - (days * 24 * 3600)
    
    url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock"
    params = {
        "symbol": ticker.upper(),
        "resolution": "1",
        "from": start_time,
        "to": end_time
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if 't' not in data or len(data['t']) == 0:
            return None
            
        df = pd.DataFrame({
            'date': [datetime.fromtimestamp(t).date() for t in data['t']],
            'open': data['o'],
            'high': data['h'],
            'low': data['l'],
            'close': data['c'],
            'volume': data['v']
        })
        
        df.set_index('date', inplace=True)
        df.sort_index(ascending=True, inplace=True)
        
        return df
        
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu {ticker}: {e}")
        return None

def get_vn30_list():
    """
    Trả về danh sách các mã cổ phiếu trong rổ VN30.
    """
    return [
        "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
        "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
        "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
    ]

