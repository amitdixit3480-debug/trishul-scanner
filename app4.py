import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="महाकाल ऑरेकल 14.0", layout="wide")

st.title("🔱 महाकाल: The Oracle (Cycle Discovery)")

# --- डिस्कवरी पैरामीटर्स ---
with st.sidebar:
    st.header("⚙️ फिल्टर सेटिंग्स")
    ticker = st.text_input("स्टॉक टिकर", "BDL.NS").upper()
    n_days = st.slider("साइकिल की अवधि (N Days)", 20, 120, 60)
    min_win = st.slider("न्यूनतम जीत दर (%)", 70, 100, 90)
    history_years = st.number_input("इतिहास (वर्ष)", 5, 20, 10)

if st.button("🚩 ब्रह्मांडीय चक्र की खोज शुरू करें"):
    try:
        with st.spinner('गहन डेटा विश्लेषण चल रहा है...'):
            data = yf.download(ticker, period=f"{history_years+2}y", interval="1d", auto_adjust=True, progress=False)
            if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
            
            discovery = []
            # साल के हर 3 दिन के अंतराल पर चेक करना (बारीकी के लिए)
            for start_day in range(1, 366 - n_days, 3):
                rets = []
                drawdowns = []
                
                for yr in range(datetime.now().year - history_years, datetime.now().year):
                    try:
                        base = datetime(yr, 1, 1) + timedelta(days=start_day)
                        sd = data.index.asof(base)
                        ed = data.index.asof(base + timedelta(days=n_days))
                        
                        if sd and ed and sd != ed:
                            window = data.loc[sd:ed]
                            # रिटर्न कैलकुलेशन
                            r = ((window.iloc[-1]['Close'] - window.iloc[0]['Open']) / window.iloc[0]['Open']) * 100
                            rets.append(r)
                            # ड्राडाउन (साइकिल के दौरान रिस्क)
                            dd = ((window['Low'].min() - window.iloc[0]['Open']) / window.iloc[0]['Open']) * 100
                            drawdowns.append(dd)
                    except: continue
                
                if len(rets) >= history_years - 2:
                    win_rate = (sum(1 for x in rets if x > 0) / len(rets)) * 100
                    if win_rate >= min_win:
                        s_dt = (datetime(2024, 1, 1) + timedelta(days=start_day)).strftime("%d-%b")
                        e_dt = (datetime(2024, 1, 1) + timedelta(days=start_day + n_days)).strftime("%d-%b")
                        
                        discovery.append({
                            "Start": s_dt,
                            "End": e_dt,
                            "Win %": f"{int(win_rate)}%",
                            "Avg Ret": round(np.mean(rets), 2),
                            "Stability (SD)": round(np.std(rets), 2),
                            "Worst Drawdown": round(min(drawdowns), 2),
                            "Median Ret": round(np.median(rets), 2)
                        })

            if discovery:
                res_df = pd.DataFrame(discovery).sort_values(by="Avg Ret", ascending=False)
                
                # विजुअल कार्ड्स
                top = res_df.iloc[0]
                c1, c2, c3 = st.columns(3)
                c1.metric("सर्वश्रेष्ठ साइकिल", f"{top['Start']} से {top['End']}")
                c2.metric("औसत लाभ", f"{top['Avg Ret']}%")
                c3.metric("स्थिरता (SD)", top['Stability (SD)'], delta_color="inverse")

                st.subheader("📊 टॉप डिस्कवर्ड साइकिल्स (Sorted by Profit)")
                st.dataframe(res_df.head(15), use_container_width=True)
                
                st.info("💡 **Stability (SD)** जितना कम होगा, साइकिल उतनी ही भरोसेमंद होगी।")
            else:
                st.warning("कोई पुख्ता साइकिल नहीं मिली। पैरामीटर्स ढीले करें।")

    except Exception as e:
        st.error(f"सिस्टम एरर: {e}")
        
