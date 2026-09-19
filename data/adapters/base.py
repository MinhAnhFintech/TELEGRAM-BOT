import pandas as pd
from abc import ABC, abstractmethod

class ExchangeAdapter(ABC):
    """Base class cho các Adapter lấy dữ liệu từ các nguồn/sàn khác nhau."""
    @abstractmethod
    def get_historical_data(self, ticker: str, days: int = 1095) -> pd.DataFrame:
        pass

# file này định nghĩa chung hành vi cho các sàn giao dịch khác nhau, 
# các adapter cụ thể sẽ kế thừa và triển khai phương thức get_historical_data để lấy dữ liệu từ nguồn tương ứng.
