import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल Pro Max", layout="wide")

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
    h1 { color: #ff4500; text-align: center; }
    /* डाउनलोड बटन का रंग हरा */
    div.stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 10px;
        border: none;
        height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Universal Cycle Scanner")

# --- स्टॉक लिस्ट डेटा ---
N50 = "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS, AXISBANK.NS, ITC.NS, KOTAKBANK.NS, LT.NS, MARUTI.NS, SUNPHARMA.NS, TITAN.NS, TATAMOTORS.NS, TATASTEEL.NS, NTPC.NS, M&M.NS, HCLTECH.NS, ASIANPAINT.NS"
N100 = N50 + ", ADANIENT.NS, ADANIPORTS.NS, BPCL.NS, COALINDIA.NS, HINDALCO.NS, IOC.NS, JSWSTEEL.NS, ONGC.NS, POWERGRID.NS, ULTRACEMCO.NS"

if 'current_list' not in st.session_state: 
    st.session_state.current_list = N50

col1, col2, col3 = st.columns(3)
if col1.button("🕉️ NIFTY 50"): st.session_state.current_list = N50
if col2.button("🔱 NIFTY 100"): st.session_state.current_list = N100
if col3.button("🔥 NIFTY 500"): st.session_state.current_list = N100 + ", RVNL.NS, IRFC.NS, ZOMATO.NS, YESBANK.NS, SUZLON.NS"

stocks_input = st.text_area("स्टॉक लिस्ट (Search or Edit)", value=st.session_state.current_list, height=100)

with st.sidebar:
    st.header("⚙️ महाकाल सेटिंग्स")
    # डायनेमिक कैलेंडर
    date_range = st.date_input("इच्छा अनुसार चक्र चुनें", [datetime(2026, 3, 1), datetime(2026, 4, 20)], format="DD/MM/YYYY")
    
    if isinstance(date_range, list) or isinstance(date_range, tuple):
        if len(date_range) == 2:
            s_d, s_m = date_range[0].day, date_range[0].month
            e_d, e_m = date_range[1].day, date_range[1].month
        else:
            st.warning("कृपया कैलेंडर में 'Start' और 'End' दोनों तारीखें चुनें।")
            st.stop()
    else:
        st.stop()
    
    st.divider()
    min_acc = st.slider("Min Accuracy %", 0, 100, 70)
    min_ret = st.slider("Min Avg Return %", 0, 20, 3)

# --- विश्लेषण शुरू ---
if st.button("🚩 महाकाल त्रिशूल विश्लेषण शुरू करें"):
    tickers = [s.strip() for s in stocks_input.split(',') if s.strip()]
    
    with st.spinner('महाकाल कृपा से डेटा स्कैन हो रहा है...'):
        all_data = yf.download(tickers, period="12y", interval="1d", progress=False, group_by='ticker')
        results, curr_yr = [], datetime.now().year

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
                    acc = (wins / len(yearly_data)) * 100
                    avg_r = sum(yearly_data.values()) / len(yearly_data)
                    
                    if acc >= min_acc and avg_r >= min_ret:
                        res_row = {"Stock": ticker.replace(".NS",""), "Accuracy": f"{int(acc)}%", "Avg Return": f"{round(avg_r, 2)}%"}
                        res_row.update(yearly_data)
                        results.append(res_row)
            except: continue

        if results:
            final_df = pd.DataFrame(results)
            
            # विजुअल कलर कोडिंग
            def color_rets(val):
                if isinstance(val, (int, float)):
                    return 'background-color: #c6efce; color: #006100;' if val > 0 else 'background-color: #ffc7ce; color: #9c0006;'
                return ''
            
            st.success(f"🔱 महाकाल की कृपा से {len(results)} जैकपॉट स्टॉक्स मिले!")
            
            # टेबल डिस्प्ले
            st.dataframe(final_df.style.applymap(color_rets, subset=final_df.columns[3:]).format(precision=2))
            
            # --- डाउनलोड बटन (Fix: सभी ब्रैकेट बंद हैं) ---
            csv_data = final_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 महाकाल त्रिशूल एक्सेल शीट डाउनलोड करें",
                data=csv_data,
                file_name=f"Mahakal_Report_{s_d}_{s_m}.csv",
                mime='text/csv'
            )
        else:
            st.error("❌ कोई स्टॉक इन फिल्टर्स में नहीं मिला।")
