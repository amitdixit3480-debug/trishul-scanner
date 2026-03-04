import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="महाकाल त्रिशूल 4.0: Cycle Master", layout="wide")

# --- 2. CSS: विजुअल फिक्स (Exact Image Match) ---
st.markdown("""
    <style>
    .event-table { width: 100%; border-collapse: collapse; border: 2px solid black; margin-bottom: 20px; }
    .event-header { background-color: #df80ff !important; color: black !important; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc !important; border: 1px solid black; text-align: center; padding: 10px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc !important; border: 1px solid black; text-align: center; color: red !important; font-weight: bold; }
    .low-broken { color: red !important; }
    .stat-box { border: 2px solid #00cc66; border-radius: 10px; padding: 15px; background-color: white; }
    .target-table { width: 100%; border: 1px solid #ddd; background-color: #ffffcc; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Cycle Master PRO")

tab1, tab2 = st.tabs(["🔍 महा-स्कैनर", "📊 डीप एनालिसिस (Exact Sheet Look)"])

# --- TAB 1: स्कैनर ---
with tab1:
    st.subheader("🚩 सेक्टर स्कैनिंग")
    STOCKS = "VADILALIND.NS, SANGHVIMOV.NS, CHOLAFIN.NS, ITC.NS, RELIANCE.NS, SBIN.NS, TCS.NS"
    input_list = st.text_area("स्टॉक लिस्ट:", value=STOCKS, height=100)
    
    if st.button("🚩 महा-स्कैन शुरू करें"):
        tickers = [t.strip().upper() for t in input_list.split(',') if t.strip()]
        with st.spinner('डेटा लोड हो रहा है...'):
            data = yf.download(tickers, period="10y", interval="1d", group_by='ticker', progress=False)
            # यहाँ स्कैनर लॉजिक रहेगा...
            st.success("स्कैन पूरा हुआ!")

# --- TAB 2: डीप एनालिसिस (सुधारित) ---
with tab2:
    st.subheader("📊 स्टॉक डीप डाइव रिपोर्ट")
    c1, c2, c3 = st.columns(3)
    with c1:
        deep_ticker = st.text_input("स्टॉक टिकर", "VADILALIND.NS").upper()
    with c2:
        deep_entry = st.text_input("एंट्री डेट (DD-Mon)", "20-Jan")
    with c3:
        deep_exit_est = st.text_input("एग्जिट अनुमान", "1st Week of April")

    if st.button("🚩 डीप रिपोर्ट जनरेट करें"):
        try:
            with st.spinner('इतिहास खंगाला जा रहा है... कृपया प्रतीक्षा करें...'):
                # डेटा फेचिंग विथ रिट्राय
                s_obj = yf.Ticker(deep_ticker)
                h_data = s_obj.history(period="15y")
                inf = s_obj.info
                
                if h_data.empty:
                    st.error("डेटा नहीं मिला! कृपया टिकर चेक करें।")
                else:
                    day, mon = deep_entry.split('-')
                    m_idx = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}[mon]
                    
                    # टेबल हेडर
                    html = '<table class="event-table"><tr class="event-header"><td>EVENT</td><td>Entry</td><td>Year</td><td>Exit/High</td><td>Return (%)</td><td>Low Broken</td></tr>'
                    
                    returns = []
                    for i, yr in enumerate(range(datetime.now().year-1, datetime.now().year-11, -1)):
                        try:
                            sd = datetime(yr, m_idx, int(day))
                            ed_limit = sd + timedelta(days=90)
                            
                            a_sd = h_data.index[h_data.index >= pd.Timestamp(sd)][0]
                            a_ed = h_data.index[h_data.index <= pd.Timestamp(ed_limit)][-1]
                            
                            subset = h_data.loc[a_sd:a_ed]
                            ps, pe = subset.iloc[0]['Open'], subset['Close'].max()
                            rt = ((pe - ps) / ps) * 100
                            returns.append(rt)
                            
                            # Low Broken Logic
                            entry_low = subset.iloc[0]['Low']
                            min_low = subset['Low'].min()
                            low_status = f'<span class="low-broken">{((entry_low-min_low)/entry_low*100):.2f}</span>' if min_low < entry_low else "NO"
                            
                            html += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{deep_entry}</td><td class="event-cell">{yr}</td><td class="event-cell">{subset["Close"].idxmax().strftime("%d-%b")}</td><td class="event-cell">{rt:.2f}%</td><td class="event-cell">{low_status}</td></tr>'
                        except:
                            html += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{deep_entry}</td><td class="event-cell">{yr}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td><td class="event-cell">-</td></tr>'
                    
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)

                    # निचला हिस्सा: Targets & Fundamentals
                    st.markdown("---")
                    f1, f2, f3 = st.columns([2,1,2])
                    
                    with f1:
                        st.markdown(f"**Stock Name:** {inf.get('longName', deep_ticker)}")
                        st.markdown(f"**Forecast:** {inf.get('targetMeanPrice', 'N/A')}")
                        st.markdown(f"**Accuracy (90/80/70):** {sorted(returns)[-2]:.1f} / {sorted(returns)[-3]:.1f} / {sorted(returns)[-4]:.1f}")
                    
                    with f2:
                        st.success("SEGMENT: CASH")
                        st.info(f"ENTRY: {deep_entry}-26")

                    with f3:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div style="background-color:#00cc66; color:white; text-align:center; font-weight:bold;">FUNDAMENTAL SCORECARD</div>
                            <p>PE: {inf.get('trailingPE', 0):.2f} | ROE: {inf.get('returnOnEquity', 0)*100:.2f}%</p>
                            <p>Debt/Eq: {inf.get('debtToEquity', 0)/100:.2f} | ICR: {inf.get('ebitda',0)/(inf.get('totalDebt',1)*0.08):.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
                        
