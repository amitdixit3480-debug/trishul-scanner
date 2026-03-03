import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# मोबाइल और डार्क मोड सेटिंग्स
st.set_page_config(page_title="🔱 GCD Trishul Pro", layout="wide")

st.markdown("<h1 style='text-align: center; color: #FFD700;'>🔱 GCD Trishul: Accuracy & Avg Ret Scanner</h1>", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def fetch_data(ticker):
    try:
        # 15 साल का डेटा ताकि टाइम साइकिल गणना सटीक रहे
        return yf.download(ticker, period="15y", interval="1d", progress=False, auto_adjust=True)
    except: return None

with st.sidebar:
    st.header("⚙️ Scanner Filters")
    s_d, s_m = st.number_input("Start Day", 1, 31, 1), st.number_input("Start Month", 1, 12, 3)
    e_d, e_m = st.number_input("End Day", 1, 31, 20), st.number_input("End Month", 1, 12, 4)
    
    st.divider()
    min_acc = st.slider("Minimum Accuracy %", 50, 100, 70)
    # नया Avg Return फ़िल्टर
    min_avg_ret = st.slider("Minimum Avg Return %", 0, 20, 3) 
    
    stocks_input = st.text_area("Stocks List (NSE)", "RELIANCE.NS, TCS.NS, INFY.NS, SBIN.NS, ICICIBANK.NS, HDFCBANK.NS, TATAMOTORS.NS, ITC.NS")
    btn = st.button("🔱 Analyze Time Cycle")

if btn:
    tickers = [x.strip() for x in stocks_input.split(',')]
    final_data = []
    prog = st.progress(0)

    for i, t in enumerate(tickers):
        df = fetch_data(t)
        if df is not None and not df.empty:
            res = {'Stock': t.replace('.NS', ''), 'Wins': 0, 'Total': 0, 'Total_Ret': 0}
            for yr in range(datetime.now().year - 10, datetime.now().year):
                try:
                    start, end = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                    p1 = df.loc[df.index >= start].iloc[0]['Open']
                    p2 = df.loc[df.index <= end].iloc[-1]['Close']
                    diff = round(((p2 - p1) / p1) * 100, 2)
                    res[str(yr)] = diff
                    if diff > 0: res['Wins'] += 1
                    res['Total'] += 1
                    res['Total_Ret'] += diff
                except: continue
            
            if res['Total'] > 0:
                acc = int((res['Wins']/res['Total'])*100)
                avg_r = round(res['Total_Ret'] / res['Total'], 2)
                
                # Accuracy और Avg Return दोनों का फ़िल्टर
                if acc >= min_acc and avg_r >= min_avg_ret:
                    res['Accuracy %'] = acc
                    res['Avg_Ret %'] = avg_r
                    final_data.append(res)
        prog.progress((i + 1) / len(tickers))

    if final_data:
        display_df = pd.DataFrame(final_data).sort_values('Avg_Ret %', ascending=False)
        st.subheader(f"📈 Results: Accuracy > {min_acc}% & Avg Ret > {min_avg_ret}%")
        
        # Avg_Ret और Accuracy को पहले दिखाना
        cols = ['Stock', 'Accuracy %', 'Avg_Ret %'] + [str(y) for y in range(datetime.now().year-10, datetime.now().year)]
        st.dataframe(display_df[cols].style.background_gradient(cmap='RdYlGn', subset=['Avg_Ret %']).format(precision=2))
    else:
        st.error("❌ कोई स्टॉक इन दोनों फिल्टर्स (Accuracy + Avg Return) में फिट नहीं बैठा।")
