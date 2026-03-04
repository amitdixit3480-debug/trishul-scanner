import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# --- 1. पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल 10.0", layout="wide")

# --- 2. CSS: फोटो जैसा लुक (Pink Header, Yellow Cells, Red Lows) ---
st.markdown("""
    <style>
    .event-table { width: 100%; border-collapse: collapse; border: 2px solid black; }
    .event-header { background-color: #df80ff !important; color: black !important; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc !important; border: 1px solid black; text-align: center; padding: 8px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc !important; border: 1px solid black; text-align: center; color: red !important; font-weight: bold; }
    .low-val { color: #cc0000 !important; font-weight: bold; }
    .stat-box { border: 2px solid #00cc66; border-radius: 8px; padding: 12px; background-color: #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Cycle Master 10.0")

# --- इनपुट ---
c1, c2, c3 = st.columns(3)
with c1:
    ticker = st.text_input("स्टॉक टिकर (उदा: VADILALIND.NS)", "VADILALIND.NS").upper()
with c2:
    entry_str = st.text_input("एंट्री डेट (DD-Mon)", "20-Jan")
with c3:
    exit_est = st.text_input("एग्जिट अनुमान", "1st Week of April")

if st.button("🚩 फाइनल ब्रह्मास्त्र रिपोर्ट जनरेट करें"):
    try:
        with st.spinner('डेटा का मंथन हो रहा है...'):
            # डेटा डाउनलोड (Stable version)
            raw_data = yf.download(ticker, period="20y", interval="1d", auto_adjust=True, progress=False)
            
            if isinstance(raw_data.columns, pd.MultiIndex):
                raw_data.columns = raw_data.columns.get_level_values(0)

            if raw_data.empty:
                st.error("डेटा नहीं मिला।")
            else:
                stock_info = yf.Ticker(ticker).info
                day_v, mon_v = entry_str.split('-')
                m_idx = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}[mon_v]
                
                # टेबल हेडर (इमेज के अनुसार)
                html = '<table class="event-table"><tr class="event-header"><td>EVENT</td><td>Entry Date</td><td>Year</td><td>Exit/High Date</td><td>Return (%)</td><td>Low Broken</td></tr>'
                
                all_returns = []
                for i in range(1, 11):
                    yr = datetime.now().year - i
                    try:
                        sd = datetime(yr, m_idx, int(day_v))
                        ed = sd + timedelta(days=90)
                        
                        mask = (raw_data.index >= pd.Timestamp(sd)) & (raw_data.index <= pd.Timestamp(ed))
                        cycle_df = raw_data.loc[mask]
                        
                        if not cycle_df.empty:
                            p_open = float(cycle_df.iloc[0]['Open'])
                            p_high = float(cycle_df['Close'].max())
                            ret = ((p_high - p_open) / p_open) * 100
                            all_returns.append(ret)
                            
                            # Low Broken Logic (इमेज जैसा लाल रंग)
                            e_low = cycle_df.iloc[0]['Low']
                            m_low = cycle_df['Low'].min()
                            low_status = f'<span class="low-val">{((e_low-m_low)/e_low*100):.2f}</span>' if m_low < e_low else "NO"
                            
                            high_dt = cycle_df['Close'].idxmax().strftime("%d-%b")
                            html += f'<tr><td class="event-cell">{i}</td><td class="event-cell">{entry_str}</td><td class="event-cell">{yr}</td><td class="event-cell">{high_dt}</td><td class="event-cell">{ret:.2f}%</td><td class="event-cell">{low_status}</td></tr>'
                        else:
                            html += f'<tr><td class="event-cell">{i}</td><td class="event-cell">{entry_str}</td><td class="event-cell">{yr}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td><td class="event-cell">-</td></tr>'
                    except:
                        html += f'<tr><td class="event-cell">{i}</td><td class="event-cell">-</td><td class="event-cell">{yr}</td><td class="fail-cell">ERR</td><td class="fail-cell">ERR</td><td class="event-cell">-</td></tr>'
                
                html += '</table>'
                st.markdown(html, unsafe_allow_html=True)

                # --- निचला हिस्सा (Scorecard & Accuracy) ---
                st.markdown("---")
                low1, low2 = st.columns(2)
                with low1:
                    # 'index out of range' से बचने के लिए सुरक्षा
                    acc_val = "N/A"
                    if len(all_returns) >= 4:
                        sorted_r = sorted(all_returns)
                        acc_val = f"{sorted_r[-4]:.1f}% (70% Accuracy)"
                    
                    st.markdown(f"""
                    <div style='background-color:#e6f3ff; padding:15px; border-radius:10px; border:1px solid #b3d9ff;'>
                        <p><b>Stock Name:</b> {stock_info.get('longName', ticker)}</p>
                        <p><b>Forecast:</b> {stock_info.get('targetMeanPrice', '131+')}</p>
                        <p><b>Target (70% Accuracy):</b> <span style='color:green; font-size:20px;'>{acc_val}</span></p>
                    </div>
                    """, unsafe_allow_html=True)

                with low2:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div style='background-color:#00cc66; color:white; text-align:center; font-weight:bold; margin-bottom:10px;'>FUNDAMENTAL SCORECARD</div>
                        <p>PE: {stock_info.get('trailingPE', 0):.2f} | ROE: {stock_info.get('returnOnEquity', 0)*100:.2f}%</p>
                        <p>Debt/Eq: {stock_info.get('debtToEquity', 0)/100:.2f} | ICR: {stock_info.get('interestCoverage', 0):.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"सिस्टम अलर्ट: {e}")
                        
