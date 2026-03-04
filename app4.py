import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- 1. पेज सेटअप ---
st.set_page_config(page_title="महाकाल मल्टी-स्कैनर 17.0", layout="wide")

st.title("🔱 महाकाल: Multi-Stock Cycle Discovery")

# --- 2. स्टॉक लिस्ट (यहीं आप अपनी लिस्ट जोड़ सकते हैं) ---
# आप यहाँ Nifty 50 या अपनी पसंद के 500 स्टॉक्स डाल सकते हैं
DEFAULT_STOCKS = "BDL.NS, HAL.NS, BEL.NS, VADILALIND.NS, NH.NS, ITC.NS, RELIANCE.NS, SBIN.NS, TCS.NS, TATAMOTORS.NS, INFOSYS.NS, MAZDOCK.NS, COCHINSHIP.NS"

with st.sidebar:
    st.header("🔍 स्कैनर सेटिंग्स")
    stock_input = st.text_area("स्टॉक लिस्ट (कॉमा से अलग करें):", value=DEFAULT_STOCKS, height=150)
    history_yrs = st.slider("इतिहास (वर्ष)", 5, 15, 8)
    min_win_rate = st.slider("Success Rate (%)", 80, 100, 90)
    
st.info("💡 यह स्कैनर हर स्टॉक के लिए 20 से 90 दिनों की सबसे बेहतरीन 'N' साइकिल खुद खोजेगा।")

if st.button("🚩 पूरी लिस्ट का महा-स्कैन शुरू करें"):
    tickers = [t.strip().upper() for t in stock_input.split(",") if t.strip()]
    all_discovery = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(tickers):
        try:
            status_text.text(f"स्कैन हो रहा है: {ticker} ({idx+1}/{len(tickers)})")
            # डेटा डाउनलोड
            data = yf.download(ticker, period=f"{history_yrs+2}y", interval="1d", auto_adjust=True, progress=False)
            
            if data.empty: continue
            if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
            
            best_for_this_stock = None
            max_score = -1
            
            # इवोल्यूशनरी स्कैन (हर स्टॉक के लिए श्रेष्ठ 'N' ढूँढना)
            for duration in range(25, 81, 5): # 25 से 80 दिन की अवधि
                for start_day in range(1, 360 - duration, 7): # हर हफ्ते के अंतराल पर चेक
                    rets = []
                    for yr in range(datetime.now().year - history_yrs, datetime.now().year):
                        try:
                            base = datetime(yr, 1, 1) + timedelta(days=start_day)
                            sd = data.index.asof(base)
                            ed = data.index.asof(base + timedelta(days=duration))
                            if sd and ed and sd != ed:
                                r = ((data.loc[ed]['Close'] - data.loc[sd]['Open']) / data.loc[sd]['Open']) * 100
                                rets.append(r)
                        except: continue
                    
                    if len(rets) >= history_yrs - 1:
                        win_rate = (sum(1 for x in rets if x > 0) / len(rets)) * 100
                        if win_rate >= min_win_rate:
                            avg_ret = np.mean(rets)
                            consistency = np.std(rets)
                            score = avg_ret / (consistency + 1)
                            
                            if score > max_score:
                                max_score = score
                                s_dt = (datetime(2024, 1, 1) + timedelta(days=start_day)).strftime("%d-%b")
                                e_dt = (datetime(2024, 1, 1) + timedelta(days=start_day + duration)).strftime("%d-%b")
                                best_for_this_stock = {
                                    "Stock": ticker,
                                    "Start Date": s_dt,
                                    "End Date": e_dt,
                                    "N Days": duration,
                                    "Win Rate": f"{int(win_rate)}%",
                                    "Avg Return": f"{avg_ret:.2f}%",
                                    "Score": round(score, 2)
                                }
            
            if best_for_this_stock:
                all_discovery.append(best_for_this_stock)
            
            progress_bar.progress((idx + 1) / len(tickers))
            
        except Exception as e:
            st.error(f"{ticker} में एरर: {e}")

    # --- परिणाम प्रदर्शन ---
    if all_discovery:
        status_text.success("🚩 महा-स्कैन पूरा हुआ!")
        final_df = pd.DataFrame(all_discovery).sort_values(by="Score", ascending=False)
        
        st.subheader("📊 खोजी गई सर्वश्रेष्ठ टाइम साइकिल्स")
        st.table(final_df) # टेबल फॉर्मेट में बेहतर दिखता है
        
        # डाउनलोड बटन
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 रिपोर्ट डाउनलोड करें", csv, "cycle_report.csv", "text/csv")
    else:
        status_text.warning("दी गई सेटिंग्स के साथ कोई पुख्ता साइकिल नहीं मिली।")
            
