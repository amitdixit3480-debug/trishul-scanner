import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल: Cycle Master PRO", layout="wide")

# --- एडवांस्ड स्टाइलिंग (इमेज मैचिंग) ---
st.markdown("""
    <style>
    .event-table { width: 100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 20px; }
    .event-header { background-color: #df80ff; color: black; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc; border: 1px solid black; text-align: center; padding: 8px; font-weight: 500; }
    .fund-header { background-color: #f2f2f2; font-weight: bold; padding: 10px; border-bottom: 2px solid black; }
    .stat-label { font-weight: bold; color: #333; }
    .stat-val { color: #d35400; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Cycle & Fundamental Analyzer")

# --- इनपुट सेक्शन ---
col_in1, col_in2, col_in3 = st.columns([2,1,1])
with col_in1:
    ticker_input = st.text_input("स्टॉक टिकर डालें (जैसे: VADILALIND.NS)", "VADILALIND.NS")
with col_in2:
    entry_date_str = st.text_input("एंट्री डेट (DD-Mon)", "20-Jan")
with col_in3:
    exit_target_str = st.text_input("एग्जिट अनुमान", "1st Week of April")

if st.button("🚩 ब्रह्मास्त्र स्कैन शुरू करें"):
    try:
        with st.spinner('डेटा प्रोसेस हो रहा है...'):
            stock = yf.Ticker(ticker_input)
            info = stock.info
            hist = stock.history(period="12y")
            
            # --- 1. साइकिल एनालिसिस (इमेज जैसा टेबल) ---
            st.subheader(f"📊 {ticker_input} ऐतिहासिक चक्र")
            
            day, mon_name = entry_date_str.split('-')
            months_map = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
            m_num = months_map[mon_name]
            
            html_cycle = '<table class="event-table"><tr class="event-header"><td>EVENT</td><td>Entry Date</td><td>Year</td><td>Exit/High</td><td>Return (%)</td><td>Weekend</td></tr>'
            
            curr_yr = datetime.now().year
            returns = []
            
            for i, yr in enumerate(range(curr_yr-1, curr_yr-11, -1)):
                try:
                    sd = datetime(yr, m_num, int(day))
                    ed = sd + pd.Timedelta(days=75) # 75 दिन का चक्र
                    
                    s_idx = hist.index.asof(sd)
                    e_idx = hist.index.asof(ed)
                    
                    p_start = hist.loc[s_idx]['Open']
                    p_end = hist.loc[e_idx]['Close']
                    ret = ((p_end - p_start) / p_start) * 100
                    is_wknd = "YES" if sd.weekday() >= 5 else "NO"
                    
                    html_cycle += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{entry_date_str}</td><td class="event-cell">{yr}</td><td class="event-cell">MID-APR</td><td class="event-cell">{ret:.2f}%</td><td class="event-cell">{is_wknd}</td></tr>'
                    returns.append(ret)
                except: continue
            
            html_cycle += '</table>'
            st.markdown(html_cycle, unsafe_allow_html=True)

            # --- 2. मजबूत फंडामेंटल ऑटोमेशन (इमेज से बेहतर) ---
            st.markdown("---")
            f1, f2, f3 = st.columns([1.5, 1, 1.5])
            
            with f1:
                st.markdown(f"""
                <div style="border:1px solid black; padding:10px; background-color:#fff;">
                    <div class="fund-header">GENERAL INFO</div>
                    <p><b>Stock:</b> {info.get('longName', 'N/A')}</p>
                    <p><b>Sector:</b> {info.get('sector', 'N/A')}</p>
                    <p><b>Current Price:</b> ₹{info.get('currentPrice', 'N/A')}</p>
                    <p><b>Market Cap:</b> ₹{info.get('marketCap', 0)//10**7} Cr.</p>
                </div>
                """, unsafe_allow_html=True)

            with f2:
                # फॉरकास्ट और सेगमेंट
                st.metric("FORECAST (Avg Target)", f"₹{info.get('targetMeanPrice', 'N/A')}")
                st.info("SEGMENT: CASH")
                acc_70 = sum(1 for r in returns if r > 0) / len(returns) * 100 if returns else 0
                st.metric("HISTORICAL ACCURACY", f"{int(acc_70)}%")

            with f3:
                # इमेज वाला सटीक फंडामेंटल टेबल
                pe = info.get('trailingPE', 0)
                peg = info.get('pegRatio', 0)
                roe = info.get('returnOnEquity', 0) * 100
                de = info.get('debtToEquity', 0) / 100
                icr = info.get('ebitda', 0) / (info.get('totalDebt', 1) * 0.08) # Estimating Interest Cover

                st.markdown(f"""
                <div style="border:2px solid black; padding:10px; border-radius:5px;">
                    <div class="fund-header" style="background-color:#00cc66; color:white;">🔱 FUNDAMENTAL SCORECARD</div>
                    <table style="width:100%; margin-top:10px;">
                        <tr><td class="stat-label">P/E Ratio:</td><td class="stat-val">{pe:.2f}</td></tr>
                        <tr><td class="stat-label">PEG Ratio:</td><td class="stat-val">{peg:.2f}</td></tr>
                        <tr><td class="stat-label">ROE (%):</td><td class="stat-val">{roe:.2f}%</td></tr>
                        <tr><td class="stat-label">Debt/Equity:</td><td class="stat-val">{de:.2f}</td></tr>
                        <tr><td class="stat-label">Int. Coverage:</td><td class="stat-val">{icr:.2f}</td></tr>
                        <tr><td class="stat-label">Industry PE:</td><td class="stat-val">{info.get('forwardPE', 'N/A')}</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"त्रुटि: {e}. कृपया टिकर (e.g. RELIANCE.NS) सही डालें।")
        
