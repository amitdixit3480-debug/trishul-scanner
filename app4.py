import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Page Setup for Mobile
st.set_page_config(page_title="Trishul Time Cycle", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; background-color: #FF4B4B; color: white; }
    .reportview-container { background: #0E1117; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 GCD Trishul: Time Cycle Pro")

# --- Performance Caching ---
@st.cache_data(ttl=3600) # 1 घंटे तक डेटा बार-बार डाउनलोड नहीं होगा
def get_data(tickers):
    data = yf.download(tickers, period="12y", interval="1d", progress=False, group_by='ticker')
    return data

# --- Sidebar Filters ---
with st.sidebar:
    st.header("⚙️ Cycle Settings")
    s_d = st.number_input("Start Day", 1, 31, 1)
    s_m = st.number_input("Start Month", 1, 12, 3)
    e_d = st.number_input("End Day", 1, 31, 20)
    e_m = st.number_input("End Month", 1, 12, 4)
    
    min_acc = st.slider("Min Win Rate (%)", 50, 100, 70)
    min_ret = st.slider("Min Avg Return (%)", 1, 20, 3)
    
    # NIFTY 500 Sample (More stocks)
    nifty_universe = "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS, AXISBANK.NS, ITC.NS, KOTAKBANK.NS, LT.NS, MARUTI.NS, SUNPHARMA.NS, TITAN.NS, TATAMOTORS.NS"
    stocks_input = st.text_area("Stock List", value=nifty_universe, height=150)

# --- Analysis Logic ---
if st.button("🔱 Analyze Time Cycle"):
    tickers = [s.strip() for s in stocks_input.split(',')]
    all_data = get_data(tickers)
    final_results = []
    
    curr_yr = datetime.now().year
    
    for ticker in tickers:
        try:
            df = all_data[ticker] if len(tickers) > 1 else all_data
            if df.empty: continue
            
            wins, total_ret = 0, []
            
            for yr in range(curr_yr - 10, curr_yr):
                try:
                    # Time Cycle Matching
                    sd, ed = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                    # Nearest Trading Day
                    si = df.index.asof(sd)
                    ei = df.index.asof(ed)
                    
                    if si and ei:
                        ret = ((df.loc[ei]['Close'] - df.loc[si]['Open']) / df.loc[si]['Open']) * 100
                        total_ret.append(ret)
                        if ret > 0: wins += 1
                except: continue
                
            if total_ret:
                wr = (wins / len(total_ret)) * 100
                avg_r = sum(total_ret) / len(total_ret)
                
                if wr >= min_acc and avg_r >= min_ret:
                    final_results.append({
                        "Stock": ticker.replace(".NS", ""),
                        "Win Rate": f"{int(wr)}%",
                        "Avg Return": f"{round(avg_r, 2)}%"
                    })
        except: continue

    if final_results:
        st.success(f"🎯 {len(final_results)} जैकपॉट स्टॉक्स मिले!")
        st.table(pd.DataFrame(final_results))
    else:
        st.error("❌ कोई स्टॉक इन दोनों फिल्टर्स में फिट नहीं बैठा।")
        
