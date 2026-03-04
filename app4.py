import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- 1. पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="महाकाल त्रिशूल 6.0", layout="wide")

# --- 2. CSS: विजुअल फिक्स (Exact Excel Look) ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .event-table { width: 100%; border-collapse: collapse; border: 2px solid black; background-color: white; }
    .event-header { background-color: #df80ff !important; color: black !important; font-weight: bold; text-align: center; border: 1px solid black; font-size: 16px; }
    .event-cell { background-color: #ffffcc !important; border: 1px solid black; text-align: center; padding: 10px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc !important; border: 1px solid black; text-align: center; color: red !important; font-weight: bold; }
    .stat-box { border: 2px solid #00cc66; border-radius: 10px; padding: 15px; background-color: white; color: black; box-shadow: 2px 2px 5px #ccc; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Cycle Master 6.0")

# --- इनपुट सेक्शन ---
col_in1, col_in2, col_in3 = st.columns(3)
with col_in1:
    ticker = st.text_input("स्टॉक टिकर (e.g. VADILALIND.NS)", "VADILALIND.NS").upper()
with col_in2:
    entry_str = st.text_input("एंट्री डेट (उदा: 20-Jan)", "20-Jan")
with col_in3:
    exit_label = st.text_input("एग्जिट अनुमान", "30-Apr")

if st.button("🚩 ब्रह्मास्त्र स्कैन शुरू करें"):
    try:
        with st.spinner('डेटा लोड हो रहा है...'):
            # डेटा डाउनलोड (मजबूत तरीका)
            raw_data = yf.download(ticker, period="20y", interval="1d", progress=False)
            
            if raw_data.empty:
                st.error(f"क्षमा करें, {ticker} के लिए डेटा नहीं मिला। टिकर चेक करें।")
            else:
                stock_info = yf.Ticker(ticker).info
                day, mon_name = entry_str.split('-')
                months = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
                m_idx = months[mon_name]
                
                # टेबल हेडर
                html = '<table class="event-table"><tr class="event-header"><td>EVENT</td><td>Entry Date</td><td>Year</td><td>Exit/High</td><td>Return (%)</td><td>Weekend</td></tr>'
                
                results_list = []
                current_year = datetime.now().year
                
                # पिछले 10 साल का लूप
                for i in range(1, 11):
                    target_year = current_year - i
                    try:
                        sd = datetime(target_year, m_idx, int(day))
                        ed = sd + timedelta(days=90) # 90 दिन का औसत चक्र
                        
                        # मार्केट के दिनों को खोजना
                        mask = (raw_data.index >= pd.Timestamp(sd)) & (raw_data.index <= pd.Timestamp(ed))
                        cycle_df = raw_data.loc[mask]
                        
                        if not cycle_df.empty:
                            p_open = cycle_df.iloc[0]['Open']
                            p_high_close = cycle_df['Close'].max() # चक्र का सबसे उच्चतम क्लोजिंग
                            ret = ((p_high_close - p_open) / p_open) * 100
                            results_list.append(ret)
                            
                            is_wknd = "YES" if sd.weekday() >= 5 else "NO"
                            high_date = cycle_df['Close'].idxmax().strftime("%d-%b")
                            
                            html += f'<tr><td class="event-cell">{i}</td><td class="event-cell">{entry_str}</td><td class="event-cell">{target_year}</td><td class="event-cell">{high_date}</td><td class="event-cell">{ret:.2f}%</td><td class="event-cell">{is_wknd}</td></tr>'
                        else:
                            raise ValueError
                    except:
                        html += f'<tr><td class="event-cell">{i}</td><td class="event-cell">{entry_str}</td><td class="event-cell">{target_year}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td><td class="event-cell">-</td></tr>'
                
                html += '</table>'
                st.markdown(html, unsafe_allow_html=True)

                # --- फंडामेंटल और एक्यूरेसी (Fixing index error) ---
                st.markdown("---")
                f1, f2 = st.columns(2)
                
                with f1:
                    accuracy_70 = "Pending"
                    if len(results_list) >= 4:
                        sorted_res = sorted(results_list)
                        accuracy_70 = f"{sorted_res[-4]:.2f}%"
                    
                    st.markdown(f"""
                    <div class="stat-box">
                        <h3 style='color:#0066cc;'>📊 Cycle Insights</h3>
                        <p><b>Stock:</b> {stock_info.get('longName', ticker)}</p>
                        <p><b>70% Accuracy Target:</b> {accuracy_70}</p>
                        <p><b>Segment:</b> CASH</p>
                    </div>
                    """, unsafe_allow_html=True)

                with f2:
                    st.markdown(f"""
                    <div class="stat-box">
                        <h3 style='color:#00cc66;'>🔱 Fundamentals</h3>
                        <p>PE: {stock_info.get('trailingPE', 0):.2f} | ROE: {stock_info.get('returnOnEquity', 0)*100:.2f}%</p>
                        <p>Debt/Eq: {stock_info.get('debtToEquity', 0)/100:.2f} | M-Cap: {stock_info.get('marketCap', 0)//10**7} Cr.</p>
                    </div>
                    """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"सिस्टम एरर: {e}. कृपया सुनिश्चित करें कि टिकर में .NS लगा है और तारीख 20-Jan जैसा है।")
                
