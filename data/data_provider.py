import pandas as pd
from pathlib import Path
import sys

from .adapters import ExchangeAdapter, DNSEAdapter, TCBSAdapter, VNDirectAdapter

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

output_dir = Path("data/output")
output_dir.mkdir(parents=True, exist_ok=True)

class DataProviderManager:
    """Quản lý việc chuyển đổi giữa các Adapter."""
    def __init__(self, default_adapter: ExchangeAdapter = None):
        self._adapter = default_adapter or DNSEAdapter()
        # Danh sách các adapter có sẵn để fallback
        self._available_adapters = [DNSEAdapter(), TCBSAdapter(), VNDirectAdapter()]

    def set_adapter(self, adapter: ExchangeAdapter):
        self._adapter = adapter
        
    def get_adapter_name(self) -> str:
        return self._adapter.__class__.__name__

    def get_historical_data(self, ticker: str, days: int = 1095) -> pd.DataFrame:
        # Thử lấy dữ liệu từ sàn hiện tại
        df = self._adapter.get_historical_data(ticker, days)
        if df is not None and len(df) > 0:
            return df
            
        print(f"Không lấy được dữ liệu từ {self.get_adapter_name()} cho {ticker}. Đang chuyển sang thử các sàn khác...")
        
        # Nếu lỗi, fallback sang các sàn khác
        for adapter in self._available_adapters:
            # Bỏ qua sàn hiện tại vì đã thử và lỗi
            if type(adapter) == type(self._adapter):
                continue
                
            print(f"Đang thử lấy dữ liệu từ {adapter.__class__.__name__}...")
            df = adapter.get_historical_data(ticker, days)
            if df is not None and len(df) > 0:
                print(f"Lấy dữ liệu thành công từ {adapter.__class__.__name__}. Đã tự động chuyển đổi mặc định sang {adapter.__class__.__name__}.")
                self.set_adapter(adapter)
                return df
                
        print(f"Lỗi: Không thể lấy dữ liệu cho {ticker} từ bất kỳ sàn nào.")
        return None

# Đối tượng toàn cục để các file khác (như bot.py) gọi mà không phá vỡ logic cũ
data_manager = DataProviderManager(DNSEAdapter())

def switch_exchange(exchange_name: str):
    """Đổi nguồn dữ liệu (DNSE, TCBS hoặc VNDIRECT)"""
    name = exchange_name.upper()
    if name == "DNSE":
        data_manager.set_adapter(DNSEAdapter())
    elif name == "TCBS":
        data_manager.set_adapter(TCBSAdapter())
    elif name == "VNDIRECT":
        data_manager.set_adapter(VNDirectAdapter())
    else:
        raise ValueError(f"Sàn/Nguồn dữ liệu {exchange_name} chưa được hỗ trợ.")

def get_current_exchange() -> str:
    return data_manager.get_adapter_name().replace('Adapter', '')

def get_historical_data(ticker: str, days: int = 1095) -> pd.DataFrame:
    """Hàm proxy gọi đến adapter hiện tại."""
    return data_manager.get_historical_data(ticker, days)

def get_vn30_list():
    """Trả về danh sách các mã cổ phiếu trong rổ VN30."""
    return [
        "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
        "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
        "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
    ]

def get_csv_VN30():
    vn30 = get_vn30_list()
    for i in range(30):
        df = get_historical_data(ticker=vn30[i])
        if df is not None:
            file_path = output_dir / f"{vn30[i]}.csv"
            df.to_csv(file_path, index=True, encoding="utf-8-sig")
            print(f"Lưu thành công {vn30[i]}.csv")

if __name__ == "__main__":
    # Test thử chuyển sàn
    print(f"Đang dùng sàn: {get_current_exchange()}")
    df_dnse = get_historical_data("FPT", days=5)
    print(df_dnse)
    
    print("\nChuyển sang TCBS...")
    switch_exchange("TCBS")
    print(f"Đang dùng sàn: {get_current_exchange()}")
    df_tcbs = get_historical_data("FPT", days=5)
    print(df_tcbs)

    print("\nChuyển sang VNDIRECT...")
    switch_exchange("VNDIRECT")
    print(f"Đang dùng sàn: {get_current_exchange()}")
    df_vnd = get_historical_data("FPT", days=5)
    print(df_vnd)