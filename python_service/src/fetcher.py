import ccxt
import pandas as pd
from datetime import datetime

class CryptoFetcher:
    def __init__(self, symbol='BTC/USDT', timeframe='1m', limit=100):
        """
        Initializes the fetcher with a specific symbol and timeframe.
        """
        # Using Binance as the data source (public API)
        self.exchange = ccxt.binance()
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit

    def get_data(self):
        """
        Fetches OHLCV (Open, High, Low, Close, Volume) data.
        Returns a Pandas DataFrame.
        """
        try:
            # Fetch raw data (timestamp, open, high, low, close, volume)
            ohlcv = self.exchange.fetch_ohlcv(
                self.symbol, 
                self.timeframe, 
                limit=self.limit
            )
            
            # Convert to DataFrame for easier handling in Python
            df = pd.DataFrame(
                ohlcv, 
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to readable date
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            print(f"Fetched {len(df)} rows for {self.symbol}")
            return df
            
        except Exception as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()

# Quick test block
if __name__ == "__main__":
    fetcher = CryptoFetcher()
    data = fetcher.get_data()
    print(data.tail())
