import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="महाकाल ऑटो-डिटेक्ट 15.0", layout="wide")

st.title("🔱 महाकाल: Auto-Cycle Detection Engine")
st.markdown("यह सिस्टम खुद खोजेगा कि स्टॉक के लिए **कितने दिनों की अवधि** और **कौन सी तारीख** सबसे सटीक है।")

# --- ऑटो-डिटेक्ट पैरामीटर्स ---
with st.sidebar:
    st.header("⚙️ स्कैन सेटिंग्स")
    ticker = st.text_input("स्टॉक टिकर", "BDL.NS").upper()
    min_win_rate = st.slider("न्यूनतम जीत दर (%)", 80, 100, 90)
    history_years = st.number_input("इतिहास (वर्ष)", 5, 20, 10)

if st.button("🚩 ऑटो-साइकिल स्कैन शुरू करें"):
    try:
        with st.spinner('हजारों समय-चक्रों का मंथन किया जा रहा है... इसमें थोड़ा समय लग सकता है...'):
            data = yf.download(ticker, period=f"{history_years+2}y", interval="1d", auto_adjust=True, progress=False)
            if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
            
            best_cycles = []
            
            # ऑटो-डिटेक्ट लॉजिक: 
            # 1. हम 30 दिन से 100 दिन तक की अलग-अलग अवधि (Durations) चेक करेंगे
            # 2. हम साल के हर 5वें दिन से स्टार्ट डेट चेक करेंगे
            for duration in range(30, 101, 10): # 30, 40, 50... 100 दिनों की साइकिल टेस्ट करें
                for start_day in range(1, 366 - duration, 5):
                    rets = []
                    
                    for yr in range(datetime.now().year - history_years, datetime.now().year):
                        try:
                            base = datetime(yr, 1, 1) + timedelta(days=start_day)
                            sd = data.index.asof(base)
                            ed = data.index.asof(base + timedelta(days=duration))
                            
                            if sd and ed and sd != ed:
                                p_start = float(data.loc[sd]['Open'])
                                p_end = float(data.loc[ed]['Close'])
                                r = ((p_end - p_start) / p_start) * 100
                                rets.append(r)
                        except: continue
                    
                    if len(rets) >= history_years - 1:
                        win_rate = (sum(1 for x in rets if x > 0) / len(rets)) * 100
                        if win_rate >= min_win_rate:
                            avg_ret = np.mean(rets)
                            if avg_ret > 10: # कम से कम 10% औसत रिटर्न वाली साइकिल ही दिखाएं
                                s_dt = (datetime(2024, 1, 1) + timedelta(days=start_day)).strftime("%d-%b")
                                e_dt = (datetime(2024, 1, 1) + timedelta(days=start_day + duration)).strftime("%d-%b")
                                
                                best_cycles.append({
                                    "अवधि (Days)": duration,
                                    "प्रारंभ तिथि": s_dt,
                                    "समाप्ति तिथि": e_dt,
                                    "Win Rate": f"{int(win_rate)}%",
                                    "Avg Return": round(avg_ret, 2),
                                    "Consistency (SD)": round(np.std(rets), 2)
                                })

            if best_cycles:
                res_df = pd.DataFrame(best_cycles).sort_values(by=["Avg Return", "Consistency (SD)"], ascending=[False, True])
                
                st.subheader(f"✅ {ticker} के लिए खोजे गए सर्वश्रेष्ठ 'Natural Cycles'")
                st.dataframe(res_df.head(20), use_container_width=True)
                
                st.success(f"सिस्टम ने पाया कि {ticker} में सबसे मजबूत व्यवहार {res_df.iloc[0]['अवधि (Days)']} दिनों की अवधि में होता है।")
            else:
                st.warning("कोई मजबूत ऑटो-साइकिल नहीं मिली। सेटिंग्स बदलें।")

    except Exception as e:
        st.error(f"सिस्टम एरर: {e}")
                                
