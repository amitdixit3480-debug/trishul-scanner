import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="महाकाल त्रिशूल Pro Max", layout="wide")

# --- विजुअल स्टाइलिंग ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-image: linear-gradient(to right, #800000, #ff4500, #ff8c00); color: white; border: none; font-weight: bold; font-size: 18px; }
    .stDataFrame { border: 2px solid #ff4500; border-radius: 15px; }
    h1 { color: #ff4500; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Universal Cycle Scanner")

# --- स्टॉक लिस्ट ---
N50 = "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS, AXISBANK.NS, ITC.NS, KOTAKBANK.NS, LT.NS, MARUTI.NS, SUNPHARMA.NS, TITAN.NS, TATAMOTORS.NS, TATASTEEL.NS, NTPC.NS, M&M.NS, HCLTECH.NS, ASIANPAINT.NS"
N100 = N50 + ", ADANIENT.NS, ADANIPORTS.NS, BPCL.NS, COALINDIA.NS, HINDALCO.NS, IOC.NS, JSWSTEEL.NS, ONGC.NS, POWERGRID.NS, ULTRACEMCO.NS, NESTLEIND.NS, TATACONSUM.NS, WIPRO.NS"

if 'current_list' not in st.session_state: st.session_state.current_list = N50

col1, col2, col3 = st.columns(3)
if col1.button("🕉️ NIFTY 50"): st.session_state.current_list = N50
if col2.button("🔱 NIFTY 100"): st.session_state.current_list = N100
if col3.button("🔥 NIFTY 500"): st.session_state.current_list = N100 + ", RVNL.NS, IRFC.NS, ZOMATO.NS"

stocks_input = st.text_area("स्टॉक लिस्ट", value=st.session_state.current_list, height=100)

with st.sidebar:
    st.header("⚙️ महाकाल सेटिंग्स")
    date_range = st.date_input("समय चक्र चुनें", [datetime(2026, 3, 1), datetime(2026, 4, 20)], format="DD/MM/YYYY")
    if len(date_range) == 2:
        s_d, s_m = date_range[0].day, date_range[0].month
        e_d, e_m = date_range[1].day, date_range[1].month
    else: st.stop()
    min_acc = st.slider("Min Accuracy %", 0, 100, 70)
    min_ret = st.slider("Min Avg Return %", 0, 20, 3)

if st.button("🚩 महाकाल त्रिशूल विश्लेषण शुरू करें"):
    tickers = [s.strip() for s in stocks_input.split(',') if s.strip()]
    with st.spinner('स्कैनिंग...'):
        all_data = yf.download(tickers, period="12y", interval="1d", progress=False, group_by='ticker')
        results, curr_yr = [], datetime.now().year

        for ticker in tickers:
            try:
                df = all_data[ticker] if len(tickers) > 1 else all_data
                wins, yearly_data = 0, {}
                for yr in range(curr_yr - 10, curr_yr):
                    try:
                        sd, ed = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                        si, ei = df.index.asof(sd), df.index.asof(ed)
                        if si and ei:
                            r = ((df.loc[ei]['Close'] - df.loc[si]['Open']) / df.loc[si]['Open']) * 100
                            yearly_data[str(yr)] = round(r, 2)
                            if r > 0: wins += 1
                    except: continue

                if yearly_data:
                    accuracy = (wins / len(yearly_data)) * 100
                    avg_return = sum(yearly_data.values()) / len(yearly_data)
                    if accuracy >= min_acc and avg_return >= min_ret:
                        res_row = {"Stock": ticker.replace(".NS",""), "Accuracy": f"{int(accuracy)}%", "Avg Return": f"{round(avg_return, 2)}%"}
                        res_row.update(yearly_data)
                        results.append(res_row)
            except: continue

        if results:
            final_df = pd.DataFrame(results)
            def color_rets(val):
                if isinstance(val, (int, float)):
                    return 'background-color: #c6efce; color: #006100;' if val > 0 else 'background-color: #ffc7ce; color: #9c0006;'
                return ''
            
            st.success(f"🔱 {len(results)} जैकपॉट स्टॉक्स मिले!")
            # .format(precision=2) से दशमलव के बाद केवल 2 अंक दिखेंगे
            st.dataframe(final_df.style.applymap(color_rets, subset=final_df.columns[3:]).format(precision=2))
        else: st.error("कोई स्टॉक नहीं मिला।")
