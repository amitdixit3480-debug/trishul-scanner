import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="महाकाल साइकिल डिस्कवरी", layout="wide")

st.title("🔱 महाकाल: True Cycle Behavior Discovery")
st.markdown("यह सिस्टम खुद खोजेगा कि स्टॉक में किस तारीख से किस तारीख तक 'N' दिनों की जादुई साइकिल है।")

# --- इनपुट ---
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("स्टॉक टिकर", "VADILALIND.NS").upper()
with col2:
    n_days = st.number_input("साइकिल की अवधि (N Days)", value=60)
with col3:
    min_win_rate = st.slider("Min Win Rate (%)", 70, 100, 80)

if st.button("🚩 खोज शुरू करें (Discovery Mode)"):
    try:
        with st.spinner('हजारों संभावनाओं का मिलान किया जा रहा है...'):
            # 1. डेटा लोड करना
            data = yf.download(ticker, period="12y", interval="1d", auto_adjust=True, progress=False)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # 2. साइकिल खोजने का लॉजिक
            # हम साल के हर दिन (1 से 365) को टेस्ट करेंगे कि क्या वहां से N दिनों की साइकिल बन रही है
            discovery_results = []
            
            # साल के पहले 300 दिनों को स्टार्ट डेट मानकर टेस्ट करना
            for start_day_of_year in range(1, 366 - n_days, 5): # 5-5 दिन के गैप पर चेक करेंगे (तेजी के लिए)
                wins = 0
                total_years = 0
                avg_return = 0
                returns_by_year = {}

                # पिछले 10 सालों में इस 'विंडो' को चेक करना
                for yr in range(datetime.now().year - 10, datetime.now().year):
                    try:
                        # साल के उस विशेष दिन की तारीख निकालना
                        base_date = datetime(yr, 1, 1) + timedelta(days=start_day_of_year)
                        sd = data.index.asof(base_date)
                        ed = data.index.asof(base_date + timedelta(days=n_days))
                        
                        if sd and ed and sd != ed:
                            ret = ((data.loc[ed]['Close'] - data.loc[sd]['Open']) / data.loc[sd]['Open']) * 100
                            avg_return += ret
                            total_years += 1
                            if ret > 0: wins += 1
                    except: continue
                
                if total_years > 0:
                    win_rate = (wins / total_years) * 100
                    if win_rate >= min_win_rate:
                        start_date_sample = (datetime(2024, 1, 1) + timedelta(days=start_day_of_year)).strftime("%d-%b")
                        end_date_sample = (datetime(2024, 1, 1) + timedelta(days=start_day_of_year + n_days)).strftime("%d-%b")
                        discovery_results.append({
                            "Start Date": start_date_sample,
                            "End Date": end_date_sample,
                            "Win Rate": f"{int(win_rate)}%",
                            "Avg Return": round(avg_return/total_years, 2),
                            "Years Tested": total_years
                        })

            # 3. रिजल्ट्स दिखाना
            if discovery_results:
                df_res = pd.DataFrame(discovery_results).sort_values(by="Avg Return", ascending=False)
                st.subheader(f"🚩 {ticker} के लिए सर्वश्रेष्ठ टाइम साइकिल्स")
                st.dataframe(df_res.head(10), use_container_width=True)
                
                st.success("ऊपर दी गई तारीखें वे हैं जहाँ पिछले 10 सालों में स्टॉक ने सबसे ज्यादा बार पॉजिटिव रिटर्न दिया है।")
            else:
                st.warning("इस 'N' अवधि के लिए कोई मजबूत साइकिल नहीं मिली। कृपया अवधि बदलें।")

    except Exception as e:
        st.error(f"Error: {e}")
                    
