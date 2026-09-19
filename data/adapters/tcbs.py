import requests
import pandas as pd
import time
from .base import ExchangeAdapter

class TCBSAdapter(ExchangeAdapter):
    """Adapter lấy dữ liệu từ TCBS (Techcom Securities)"""
    def get_historical_data(self, ticker: str, days: int = 1095) -> pd.DataFrame:
        end_time = int(time.time())
        start_time = end_time - (days * 24 * 3600)
        
        url = "https://apipubaws.tcbs.com.vn/stock-insight/v1/stock/bars-long-term"
        params = {
            "ticker": ticker.upper(),
            "type": "stock",
            "resolution": "D",
            "from": start_time,
            "to": end_time
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'data' not in data or len(data['data']) == 0:
                return None
                
            df = pd.DataFrame(data['data'])
            # TCBS API trả về chuỗi ISO cho tradingDate, ví dụ: '2023-01-01T00:00:00.000Z'
            df['date'] = pd.to_datetime(df['tradingDate']).dt.date
            df.set_index('date', inplace=True)
            df.sort_index(ascending=True, inplace=True)
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"Lỗi khi lấy dữ liệu {ticker} từ TCBS: {e}")
            return None

