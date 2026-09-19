import requests
import pandas as pd
import time
from datetime import datetime
from .base import ExchangeAdapter

class VNDirectAdapter(ExchangeAdapter):
    """Adapter lấy dữ liệu từ VNDirect"""
    def get_historical_data(self, ticker: str, days: int = 1095) -> pd.DataFrame:
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 3600)
        
        url = "https://dchart-api.vndirect.com.vn/dchart/history"
        params = {
            "symbol": ticker.upper(),
            "resolution": "D",
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
            print(f"Lỗi khi lấy dữ liệu {ticker} từ VNDirect: {e}")
            return None

