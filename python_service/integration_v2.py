import requests
from src.fetcher import CryptoFetcher

JULIA_URL = "http://localhost:8080"

def run_pipeline():
    # 1. Get Real Data (Python)
    print("--- 1. Python: Fetching Data from Binance ---")
    fetcher = CryptoFetcher(limit=20) # Small batch for testing
    df = fetcher.get_data()
    
    if df.empty:
        print("Stopping: No data fetched.")
        return

    # Extract closing prices and convert to list of floats
    prices = df['close'].tolist()
    print(f"Sent {len(prices)} candles. Last price: {prices[-1]}")

    # 2. Send to Julia (API)
    print("\n--- 2. Sending to Julia for Processing ---")
    payload = {"prices": prices}
    
    try:
        response = requests.post(f"{JULIA_URL}/process", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("Success! Julia Response:")
            print(f"SMA Values (Last 5): {result['sma_values'][-5:]}")
        else:
            print(f"Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    run_pipeline()
