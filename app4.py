import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- पेज सेटअप (Premium Mobile Look) ---
st.set_page_config(page_title="महाकाल त्रिशूल Pro Max", layout="wide")

# --- विजुअल स्टाइलिंग (Dark Theme with Gold & Red) ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background-image: linear-gradient(to right, #800000, #ff4500, #ff8c00); 
        color: white; 
        border: none; 
        font-weight: bold;
        font-size: 18px;
    }
    .stDataFrame { border: 2px solid #ff4500; border-radius: 15px; }
    h1 { color: #ff4500; text-align: center; font-family: 'Segoe UI'; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Universal Cycle Scanner")

# --- स्टॉक लिस्ट डेटा (Pre-loaded for Buttons) ---
N50 = "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS, AXISBANK.NS, ITC.NS, KOTAKBANK.NS, LT.NS, MARUTI.NS, SUNPHARMA.NS, TITAN.NS, TATAMOTORS.NS, TATASTEEL.NS, NTPC.NS, M&M.NS, HCLTECH.NS, ASIANPAINT.NS"
N100 = N50 + ", ADANIENT.NS, ADANIPORTS.NS, BPCL.NS, COALINDIA.NS, HINDALCO.NS, IOC.NS, JSWSTEEL.NS, ONGC.NS, POWERGRID.NS, ULTRACEMCO.NS, NESTLEIND.NS, TATACONSUM.NS, WIPRO.NS, APOLLOHOSP.NS, DLF.NS"
N500_SELECT = N100 + ", YESBANK.NS, ZOMATO.NS, RVNL.NS, IRFC.NS, SUZLON.NS, IDEA.NS, NHPC.NS, SJVN.NS, IREDA.NS, BHEL.NS, BEL.NS, MAZDOCK.NS, JSWENERGY.NS, POLYCAB.NS"

# --- मुख्य इंटरफ़ेस ---
st.subheader("🚩 मार्केट सेगमेंट चुनें")
col1, col2, col3 = st.columns(3)

if 'current_list' not in st.session_state:
    st.session_state.current_list = N50

if col1.button("🕉️ NIFTY 50"): st.session_state.current_list = N50
if col2.button("🔱 NIFTY 100"): st.session_state.current_list = N100
if col3.button("🔥 NIFTY 500"): st.session_state.current_list = N500_SELECT

# खाली बॉक्स: अपनी इच्छा से कोई भी स्टॉक जोड़ें
stocks_input = st.text_area("स्टॉक लिस्ट (Search or Edit)", value=st.session_state.current_list, height=100)

# --- साइडबार: डायनेमिक कैलेंडर और फिल्टर्स ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/shiva.png", width=100)
    st.header("⚙️ महाकाल सेटिंग्स")
    
    # डायनेमिक डेट पिकर (Calendar)
    date_range = st.date_input(
        "इच्छा अनुसार समय चक्र चुनें",
        [datetime(datetime.now().year, 3, 1), datetime(datetime.now().year, 4, 20)],
        format="DD/MM/YYYY"
    )

    if len(date_range) == 2:
        start_dt, end_dt = date_range
        s_d, s_m = start_dt.day, start_dt.month
        e_d, e_m = end_dt.day, end_dt.month
    else:
        st.warning("कैलेंडर में दोनों तारीखें चुनें।")
        st.stop()

    st.divider()
    min_acc = st.slider("न्यूनतम सटीकता (Win Rate %)", 0, 100, 70)
    min_ret = st.slider("न्यूनतम औसत रिटर्न %", 0, 20, 3)

# --- स्कैनिंग लॉजिक ---
if st.button("🚩 महाकाल त्रिशूल विश्लेषण शुरू करें"):
    tickers = [s.strip() for s in stocks_input.split(',') if s.strip()]
    
    with st.spinner('महाकाल कृपा से डेटा स्कैन हो रहा है...'):
        all_data = yf.download(tickers, period="12y", interval="1d", progress=False, group_by='ticker')
        results = []
        curr_yr = datetime.now().year

        for ticker in tickers:
            try:
                df = all_data[ticker] if len(tickers) > 1 else all_data
                if df.empty: continue
                
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

        # --- रिज़ल्ट टेबल (Color Coded like image_809e75.png) ---
        if results:
            final_df = pd.DataFrame(results)
            def color_rets(val):
                if isinstance(val, float):
                    return 'background-color: #c6efce; color: #006100;' if val > 0 else 'background-color: #ffc7ce; color: #9c0006;'
                return ''

            st.success(f"🔱 महाकाल की कृपा से {len(results)} जैकपॉट स्टॉक्स मिले!")
            st.dataframe(final_df.style.applymap(color_rets, subset=final_df.columns[3:]))
        else:
            st.error("❌ इस समय चक्र में कोई स्टॉक फिट नहीं हुआ।")
