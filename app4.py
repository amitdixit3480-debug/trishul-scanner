import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल: Ultimate Cycle Master", layout="wide")

# --- CSS: इमेज जैसा लुक ---
st.markdown("""
    <style>
    .event-header { background-color: #df80ff !important; color: black !important; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc !important; border: 1px solid black; text-align: center; padding: 8px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc !important; border: 1px solid black; text-align: center; color: red !important; font-weight: bold; }
    .stat-label { font-weight: bold; background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; color: black; }
    .stat-val { color: #d35400; font-weight: bold; text-align: right; border: 1px solid #ddd; padding: 8px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(to right, #b22222, #ff4500); color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Universal Cycle Scanner & Analyzer")

# --- टैब सिस्टम ---
tab1, tab2 = st.tabs(["🔍 महा-स्कैनर (500 Stocks)", "📊 डीप साइकिल एनालिसिस"])

# ------------------------------------------------------------------
# TAB 2: DEEP CYCLE ANALYSIS (सुधारित)
# ------------------------------------------------------------------
with tab2:
    st.subheader("📊 स्टॉक डीप डाइव (एक्सेल स्टाइल रिपोर्ट)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        # सुनिश्चित करें कि टिकर में .NS है
        t_deep = st.text_input("स्टॉक टिकर (उदा: ITC.NS)", "ITC.NS").upper()
    with col_b:
        # DD-Mon फॉर्मेट (उदा: 20-Jan)
        entry_date_str = st.text_input("एंट्री डेट (DD-Mon)", "20-Jan")
    with col_c:
        exit_label = st.text_input("एग्जिट अनुमान", "30-Apr")

    if st.button("🚩 जेनरेट चक्र रिपोर्ट"):
        try:
            with st.spinner('डेटा निकाला जा रहा है...'):
                stock_obj = yf.Ticker(t_deep)
                # 'max' की जगह '15y' का उपयोग डेटा लोडिंग को स्थिर बनाता है
                hist = stock_obj.history(period="15y")
                info = stock_obj.info
                
                if hist.empty:
                    st.error("डेटा नहीं मिला। कृपया टिकर (e.g. RELIANCE.NS) चेक करें।")
                else:
                    day, mon_name = entry_date_str.split('-')
                    m_num = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}[mon_name]
                    
                    html = '<table style="width:100%; border:1px solid black; border-collapse: collapse;">'
                    html += '<tr class="event-header"><td>EVENT</td><td>Entry Date</td><td>Year</td><td>Exit/High</td><td>Return (%)</td><td>Status</td></tr>'
                    
                    returns_list = []
                    for i, yr in enumerate(range(datetime.now().year-1, datetime.now().year-11, -1)):
                        try:
                            sd = datetime(yr, m_num, int(day))
                            ed_target = sd + timedelta(days=90) # 3 महीने का चक्र
                            
                            # नजदीकी कारोबारी दिन खोजना
                            actual_sd = hist.index[hist.index >= pd.Timestamp(sd)][0]
                            actual_ed = hist.index[hist.index <= pd.Timestamp(ed_target)][-1]
                            
                            p_start = hist.loc[actual_sd]['Open']
                            p_end = hist.loc[actual_ed]['Close']
                            ret = ((p_end - p_start) / p_start) * 100
                            returns_list.append(ret)
                            
                            html += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{entry_date_str}</td><td class="event-cell">{yr}</td><td class="event-cell">{actual_ed.strftime("%d-%b")}</td><td class="event-cell">{ret:.2f}%</td><td class="event-cell">SUCCESS</td></tr>'
                        except:
                            html += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{entry_date_str}</td><td class="event-cell">{yr}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td><td class="event-cell">-</td></tr>'
                    
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)
                    
                    # फंडामेंटल डेटा डिस्प्ले
                    st.markdown("---")
                    st.metric("Cycle Accuracy", f"{(sum(1 for r in returns_list if r > 0) / len(returns_list) * 100 if returns_list else 0):.0f}%")
        except Exception as e:
            st.error(f"Error: {e}. कृपया इनपुट फॉर्मेट चेक करें।")
            
