import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल 9.0", layout="wide")

# --- 2. CSS (इमेज जैसा लुक) ---
st.markdown("""
    <style>
    .event-table { width: 100%; border-collapse: collapse; border: 2px solid black; }
    .event-header { background-color: #df80ff !important; color: black !important; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc !important; border: 1px solid black; text-align: center; padding: 10px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc !important; border: 1px solid black; text-align: center; color: red !important; font-weight: bold; border: 1px solid black; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Cycle Master 9.0")

# --- इनपुट ---
c1, c2, c3 = st.columns(3)
with c1:
    ticker = st.text_input("स्टॉक टिकर (e.g. VADILALIND.NS)", "VADILALIND.NS").upper()
with c2:
    entry_str = st.text_input("एंट्री डेट (उदा: 20-Jan)", "20-Jan")
with c3:
    exit_label = st.text_input("एग्जिट अनुमान", "30-Apr")

if st.button("🚩 गहरी डेटा खोज शुरू करें"):
    try:
        with st.spinner('महाकाल की कृपा से सर्वर से डेटा खींचा जा रहा है... थोड़ा समय लग सकता है...'):
            # --- सुधार: yf.download को 'auto_adjust=True' और 'threads=False' के साथ प्रयोग करें ---
            # इससे डेटा आने की गारंटी बढ़ जाती है
            raw_data = yf.download(ticker, period="max", interval="1d", auto_adjust=True, progress=False, threads=False)
            
            # डेटा आने तक थोड़ा इंतजार (Artificial delay for stability)
            time.sleep(1) 

            # मल्टी-इंडेक्स कॉलम को साफ करना
            if isinstance(raw_data.columns, pd.MultiIndex):
                raw_data.columns = raw_data.columns.get_level_values(0)

            if raw_data.empty or len(raw_data) < 100:
                st.error(f"❌ डेटा डाउनलोड नहीं हो पाया! {ticker} शायद गलत है या Yahoo Finance का सर्वर धीमा है। कृपया एक बार और दबाएं।")
            else:
                st.success(f"✅ {len(raw_data)} दिनों का डेटा सफलतापूर्वक प्राप्त हुआ!")
                
                day_val, mon_name = entry_str.split('-')
                months = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
                m_idx = months[mon_name]
                
                html = '<table class="event-table"><tr class="event-header"><td>EVENT</td><td>Entry</td><td>Year</td><td>Exit/High Date</td><td>Return (%)</td></tr>'
                
                results = []
                curr_yr = datetime.now().year
                
                for i in range(1, 11):
                    yr = curr_yr - i
                    try:
                        sd = datetime(yr, m_idx, int(day_val))
                        ed = sd + timedelta(days=100)
                        
                        # इंडेक्स को टोपोलॉजी के हिसाब से काटना
                        mask = (raw_data.index >= pd.Timestamp(sd)) & (raw_data.index <= pd.Timestamp(ed))
                        cycle_df = raw_data.loc[mask]
                        
                        if not cycle_df.empty:
                            p_open = float(cycle_df.iloc[0]['Open'])
                            p_high = float(cycle_df['Close'].max())
                            ret = ((p_high - p_open) / p_open) * 100
                            results.append(ret)
                            
                            high_dt = cycle_df['Close'].idxmax().strftime("%d-%b")
                            html += f'<tr><td class="event-cell">{i}</td><td class="event-cell">{entry_str}</td><td class="event-cell">{yr}</td><td class="event-cell">{high_dt}</td><td class="event-cell">{ret:.2f}%</td></tr>'
                        else:
                            html += f'<tr><td class="event-cell">{i}</td><td class="event-cell">{entry_str}</td><td class="event-cell">{yr}</td><td class="fail-cell">NO DATA</td><td class="fail-cell">0.00%</td></tr>'
                    except:
                        html += f'<tr><td class="event-cell">{i}</td><td class="event-cell">{entry_str}</td><td class="event-cell">{yr}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td></tr>'
                
                html += '</table>'
                st.markdown(html, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"सिस्टम अलर्ट: {e}")
                    
