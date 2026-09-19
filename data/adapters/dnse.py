import requests
import pandas as pd
import time
from datetime import datetime
from .base import ExchangeAdapter

class DNSEAdapter(ExchangeAdapter):
    """Adapter lấy dữ liệu từ DNSE (Entrade)"""
    def get_historical_data(self, ticker: str, days: int = 1095) -> pd.DataFrame:
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 3600)
        
        url = f"https://services.entrade.com.vn/chart-api/v2/ohlcs/stock"
        params = {
            "symbol": ticker.upper(),
            "resolution": "30", # Nến ngày (DNSE thường coi 30 là 1D trong một số context hoặc dùng "D")
            "from": start_time,
            "to": end_time
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        
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
            print(f"Lỗi khi lấy dữ liệu {ticker} từ DNSE: {e}")
            return None

