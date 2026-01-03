import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import os
from fetcher import CryptoFetcher

# --- CONFIGURATION ---
# Get URL from Docker Env or default to localhost
JULIA_URL = os.getenv("JULIA_URL", "http://localhost:8080")

st.set_page_config(
    page_title="CryptoPulse Hybrid", 
    page_icon="⚡",
    layout="wide"
)

# --- HELPER FUNCTIONS ---

def get_julia_calculations(prices, period):
    """
    Sends raw prices to the Julia Microservice.
    Increased timeout to 60s to allow Julia JIT compilation on first run.
    """
    try:
        payload = {
            "prices": prices, 
            "period": int(period)
        }
        
        # 60s timeout handles the "Time-to-First-X" compilation delay of Julia
        response = requests.post(f"{JULIA_URL}/process", json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Julia Service Error ({response.status_code}): {response.text}")
            return {}
            
    except requests.exceptions.ReadTimeout:
        st.error("⏳ Julia is compiling... Try refreshing in 10 seconds.")
        return {}
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to Julia Service. Is the container running?")
        return {}
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return {}

# --- UI LAYOUT ---

st.title("⚡ CryptoPulse: Polyglot AI Forecasting")
st.markdown("""
**Architecture:** 

1.Python fetches live market data (Binance).

2.Julia (Flux.jl) receives data, trains a Neural Network in real-time, and predicts the next step.

3.Python visualizes the result.
""")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    symbol = st.selectbox("Crypto Pair", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT"])
    timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m"])
    st.divider()
    sma_period = st.slider("SMA Trend Period", 3, 50, 10)
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# --- MAIN EXECUTION ---

# 1. Fetch Data (Python)
with st.spinner(f"Fetching live data for {symbol}..."):
    fetcher = CryptoFetcher(symbol=symbol, timeframe=timeframe, limit=60)
    df = fetcher.get_data()

if not df.empty:
    prices = df['close'].tolist()
    
    # 2. Process Data (Julia)
    julia_response = get_julia_calculations(prices, sma_period)
    
    if julia_response:
        # Extract Data
        sma_values = julia_response.get("sma_values", [])
        forecast_price = julia_response.get("forecast_price", 0)
        training_loss = julia_response.get("training_loss", 0)
        fitted_data = julia_response.get("fitted_data", [])
        
        # --- PLOTTING ---
        fig = go.Figure()

        # A. Candlesticks (Actual Data)
        fig.add_trace(go.Candlestick(
            x=df['timestamp'],
            open=df['open'], high=df['high'],
            low=df['low'], close=df['close'],
            name='Price'
        ))

        # B. AI Model Fit (The "Learned" Pattern)
        # Note: Fitted data starts after the lookback window (index 5)
        if fitted_data:
            # Slice timestamps to match the length of fitted_data
            valid_timestamps = df['timestamp'].iloc[5:]
            # Ensure lengths match exactly to avoid Plotly errors
            limit = min(len(valid_timestamps), len(fitted_data))
            
            fig.add_trace(go.Scatter(
                x=valid_timestamps[:limit], 
                y=fitted_data[:limit],
                mode='lines',
                name='AI Model Fit (Learned)',
                line=dict(color='purple', width=2, dash='dot'),
                opacity=0.8
            ))

        # C. SMA Line
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=sma_values,
            mode='lines',
            name=f'Trend (SMA {sma_period})',
            line=dict(color='orange', width=1)
        ))
        
        # D. AI Forecast (The Future Star)
        if forecast_price > 0:
            last_ts = df['timestamp'].iloc[-1]
            future_ts = last_ts + pd.Timedelta(minutes=1) # Approx for 1m
            
            fig.add_trace(go.Scatter(
                x=[future_ts],
                y=[forecast_price],
                mode='markers+text',
                name='AI Forecast',
                marker=dict(color='#00FFFF', size=15, symbol='star'),
                text=[f"{forecast_price:.2f}"],
                textposition="top center",
                textfont=dict(color='cyan', size=12)
            ))

        fig.update_layout(
            title=f"<b>{symbol}</b> Market Analysis & AI Inference",
            yaxis_title="Price (USDT)",
            template="plotly_dark",
            height=650,
            hovermode="x unified",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)
        
        # --- METRICS ROW ---
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Current Price", f"${prices[-1]:,.2f}")
        
        diff = forecast_price - prices[-1]
        col2.metric("AI Forecast", f"${forecast_price:,.2f}", 
                    delta=f"{diff:.2f}", delta_color="normal")
        
        # Display Loss (Lower is better)
        col3.metric("Training Loss (MSE)", f"{training_loss:.5f}", 
                    help="Mean Squared Error. Closer to 0 means better fit.")
        
        # Simple convergence check
        status = "✅ Converged" if training_loss < 0.05 else "⚠️ High Variance"
        col4.metric("Model Status", status)
        
else:
    st.warning("No data received from exchange. Please try refreshing.")
