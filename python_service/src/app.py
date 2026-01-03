import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from fetcher import CryptoFetcher
import os

# --- CONFIGURATION ---
# We try to get the URL from Docker Env, otherwise fallback to localhost (for local dev)
JULIA_URL = os.getenv("JULIA_URL", "http://localhost:8080")
print(f"DEBUG: Conected in -> {JULIA_URL}", flush=True)

st.set_page_config(
    page_title="CryptoPulse Hybrid", 
    page_icon="⚡",
    layout="wide"
)

# --- HELPER FUNCTIONS ---

def get_julia_calculations(prices, period):
    """
    Sends raw prices to the Julia Microservice for SMA calculation and AI Forecasting.
    """
    try:
        # Prepare payload
        payload = {
            "prices": prices, 
            "period": int(period)
        }
        
        # Send Request
        response = requests.post(f"{JULIA_URL}/process", json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Julia Service Error ({response.status_code}): {response.text}")
            return {}
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to Julia Service. Is it running?")
        return {}
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return {}

# --- UI LAYOUT ---

st.title("⚡ CryptoPulse: Polyglot Forecasting (Python + Julia)")
st.markdown("""
**Architecture:** 

1. **Python** fetches live market data (Binance).

2. **Julia (Flux.jl)** receives data, trains a Neural Network in real-time, and predicts the next step.

3. **Python** visualizes the result.
""")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Data Settings
    symbol = st.selectbox("Crypto Pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"])
    timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h"])
    
    st.divider()
    
    # Model Settings
    st.subheader("🧠 Julia AI Settings")
    sma_period = st.slider("SMA Trend Period", min_value=3, max_value=50, value=10)
    
    st.info("Tip: Adjusting the slider triggers a re-calculation in Julia instantly.")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# --- MAIN EXECUTION ---

# 1. Fetch Data (Python side)
with st.spinner(f"Fetching live data for {symbol}..."):
    fetcher = CryptoFetcher(symbol=symbol, timeframe=timeframe, limit=60)
    df = fetcher.get_data()

if not df.empty:
    # Prepare data for Julia
    prices = df['close'].tolist()
    
    # 2. Process Data (Call Julia API)
    julia_response = get_julia_calculations(prices, sma_period)
    
    if julia_response:
        # Extract results
        sma_values = julia_response.get("sma_values", [])
        forecast_price = julia_response.get("forecast_price", 0)
        
        # --- PLOTTING ---
        fig = go.Figure()

        # A. Candlestick Chart (History)
        fig.add_trace(go.Candlestick(
            x=df['timestamp'],
            open=df['open'], high=df['high'],
            low=df['low'], close=df['close'],
            name='Price'
        ))

        # B. SMA Line (Julia Calculation)
        # Note: We plot SMA against the original timestamps. 
        # TimeSeries.jl output aligns with input length.
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=sma_values,
            mode='lines',
            name=f'Trend (SMA {sma_period})',
            line=dict(color='#FFA500', width=2) # Orange
        ))
        
        # C. AI Prediction (The "Future" Dot)
        if forecast_price > 0:
            # Create a "future" timestamp for plotting
            last_timestamp = df['timestamp'].iloc[-1]
            
            # Estimate next timestamp based on timeframe (simple logic for demo)
            # Defaulting to +1 minute if timeframe is '1m'
            future_timestamp = last_timestamp + pd.Timedelta(minutes=1)
            
            fig.add_trace(go.Scatter(
                x=[future_timestamp],
                y=[forecast_price],
                mode='markers+text',
                name='AI Forecast (Flux.jl)',
                marker=dict(color='#00FFFF', size=14, symbol='star'), # Cyan Star
                text=[f"Pred: {forecast_price:.2f}"],
                textposition="top center",
                textfont=dict(color='#00FFFF')
            ))

        # Chart Layout
        fig.update_layout(
            title=f"<b>{symbol}</b> Live Market Analysis",
            yaxis_title="Price (USDT)",
            xaxis_title="Time (UTC)",
            template="plotly_dark",
            height=650,
            hovermode="x unified",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # --- METRICS ROW ---
        col1, col2, col3, col4 = st.columns(4)
        
        current_price = prices[-1]
        price_diff = forecast_price - current_price
        
        col1.metric("Current Price", f"${current_price:,.2f}")
        
        col2.metric("Julia SMA", f"${sma_values[-1]:,.2f}", 
                    delta=f"{current_price - sma_values[-1]:.2f} (vs Trend)")
        
        col3.metric("AI Forecast (Next Candle)", f"${forecast_price:,.2f}",
                    delta=f"{price_diff:.2f}",
                    delta_color="normal")
        
        # Simple Logic for Signal
        signal = "NEUTRAL"
        if forecast_price > current_price:
            signal = "BULLISH 🚀"
        elif forecast_price < current_price:
            signal = "BEARISH 🔻"
            
        col4.metric("AI Signal", signal)
        
else:
    st.warning("No data received from exchange. Please try refreshing.")
