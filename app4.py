import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title=" AMIT Trishul Pro", layout="wide")

# --- Custom Styling (Visual Enhancement) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    .stTable { background-color: #1e1e1e; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 GCD Trishul: Universal Cycle Scanner")

# --- Indices Data ---
N50 = "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS, AXISBANK.NS, ITC.NS, KOTAKBANK.NS, LT.NS, MARUTI.NS, SUNPHARMA.NS, TITAN.NS, TATAMOTORS.NS, TATASTEEL.NS, NTPC.NS, M&M.NS, HCLTECH.NS, ASIANPAINT.NS"
N100 = N50 + ", ADANIENT.NS, ADANIPORTS.NS, BPCL.NS, COALINDIA.NS, HINDALCO.NS, IOC.NS, JSWSTEEL.NS, ONGC.NS, POWERGRID.NS, ULTRACEMCO.NS"
N500_SAMPLE = N100 + ", YESBANK.NS, ZOMATO.NS, IDEA.NS, RVNL.NS, IRFC.NS, SUZLON.NS"

# --- Sidebar Filters ---
with st.sidebar:
    st.header("⚙️ Scan Parameters")
    col1, col2 = st.columns(2)
    with col1:
        s_d = st.number_input("Start Day", 1, 31, 1)
        s_m = st.number_input("Start Month", 1, 12, 3)
    with col2:
        e_d = st.number_input("End Day", 1, 31, 20)
        e_m = st.number_input("End Month", 1, 12, 4)
    
    min_acc = st.slider("Min Accuracy (%)", 0, 100, 70)
    min_ret = st.slider("Min Avg Return (%)", 0, 20, 3)

# --- Stock List Logic ---
st.subheader("📁 Select Universe or Add Stocks")
c1, c2, c3 = st.columns(3)

# State management for buttons
if 'stock_list' not in st.session_state:
    st.session_state.stock_list = N50

if c1.button("🚀 NIFTY 50"): st.session_state.stock_list = N50
if c2.button("🌟 NIFTY 100"): st.session_state.stock_list = N100
if c3.button("🔥 NIFTY 500"): st.session_state.stock_list = N500_SAMPLE

stocks_input = st.text_area("Stocks to Scan (NSE Codes)", value=st.session_state.stock_list, height=100)

# --- Analysis ---
if st.button("🔱 Start Trishul Analysis"):
    tickers = [s.strip() for s in stocks_input.split(',')]
    with st.spinner('Scanning Market Cycles...'):
        all_data = yf.download(tickers, period="10y", interval="1d", progress=False, group_by='ticker')
        results = []
        curr_yr = datetime.now().year

        for ticker in tickers:
            try:
                df = all_data[ticker] if len(tickers) > 1 else all_data
                if df.empty: continue
                wins, annual_rets = 0, {}
                
                for yr in range(curr_yr - 10, curr_yr):
                    try:
                        sd, ed = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                        si = df.index.asof(sd)
                        ei = df.index.asof(ed)
                        ret = ((df.loc[ei]['Close'] - df.loc[si]['Open']) / df.loc[si]['Open']) * 100
                        annual_rets[str(yr)] = round(ret, 2)
                        if ret > 0: wins += 1
                    except: continue

                if annual_rets:
                    acc = (wins / len(annual_rets)) * 100
                    avg_r = sum(annual_rets.values()) / len(annual_rets)
                    
                    if acc >= min_acc and avg_r >= min_ret:
                        row = {"Stock": ticker.replace(".NS",""), "Win Rate": f"{int(acc)}%", "Avg Return": f"{round(avg_r,2)}%"}
                        row.update(annual_rets)
                        results.append(row)
            except: continue

        if results:
            res_df = pd.DataFrame(results)
            
            # --- Visual Styling (Like image_809e75.png) ---
            def color_returns(val):
                if isinstance(val, float):
                    color = '#c6efce' if val > 0 else '#ffc7ce'
                    return f'background-color: {color}; color: black'
                return ''

            st.success(f"🎯 {len(results)} जैकपॉट स्टॉक्स मिले!")
            st.dataframe(res_df.style.applymap(color_returns, subset=res_df.columns[3:]))
        else:
            st.warning("कोई स्टॉक इन फिल्टर्स में नहीं मिला। कृपया Accuracy या Return कम करके देखें।")

