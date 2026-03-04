import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- 1. पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल 5.0", layout="wide")

# --- 2. CSS (Exact Image Look) ---
st.markdown("""
    <style>
    .event-table { width: 100%; border-collapse: collapse; border: 2px solid black; }
    .event-header { background-color: #df80ff !important; color: black; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc !important; border: 1px solid black; text-align: center; padding: 10px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc !important; border: 1px solid black; text-align: center; color: red !important; font-weight: bold; border: 1px solid black; }
    .stat-box { border: 2px solid #00cc66; border-radius: 10px; padding: 15px; background-color: white; color: black; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Cycle Master (Zero Error)")

tab1, tab2 = st.tabs(["🔍 महा-स्कैनर", "📊 डीप एनालिसिस (No Error Version)"])

# --- TAB 2: डीप एनालिसिस (Fixing 'list index out of range') ---
with tab2:
    st.subheader("📊 स्टॉक डीप डाइव रिपोर्ट")
    c1, c2, c3 = st.columns(3)
    with c1:
        deep_ticker = st.text_input("स्टॉक टिकर", "VADILALIND.NS").upper()
    with c2:
        deep_entry = st.text_input("एंट्री डेट (DD-Mon)", "20-Jan")
    with c3:
        deep_exit_est = st.text_input("एग्जिट अनुमान", "30-Apr")

    if st.button("🚩 ब्रह्मास्त्र स्कैन शुरू करें"):
        try:
            with st.spinner('महाकाल की कृपा से डेटा लोड हो रहा है...'):
                s_obj = yf.Ticker(deep_ticker)
                # 15 साल का डेटा ताकि FAIL कम हो
                h_data = s_obj.history(period="15y")
                inf = s_obj.info
                
                if h_data.empty:
                    st.warning("Yahoo Finance से डेटा नहीं मिल पा रहा है। कृपया 2 मिनट बाद प्रयास करें या टिकर बदलें।")
                else:
                    day, mon = deep_entry.split('-')
                    m_idx = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}[mon]
                    
                    html = '<table class="event-table"><tr class="event-header"><td>EVENT</td><td>Entry</td><td>Year</td><td>Exit/High</td><td>Return (%)</td></tr>'
                    
                    returns = []
                    for yr in range(datetime.now().year-1, datetime.now().year-11, -1):
                        try:
                            sd = datetime(yr, m_idx, int(day))
                            ed_limit = sd + timedelta(days=90)
                            
                            # नजदीकी कारोबारी दिन ढूँढना
                            a_sd = h_data.index[h_data.index >= pd.Timestamp(sd)][0]
                            a_ed = h_data.index[h_data.index <= pd.Timestamp(ed_limit)][-1]
                            
                            subset = h_data.loc[a_sd:a_ed]
                            if not subset.empty:
                                ps = subset.iloc[0]['Open']
                                pe = subset['Close'].max()
                                rt = ((pe - ps) / ps) * 100
                                returns.append(rt)
                                
                                html += f'<tr><td class="event-cell">{len(returns)}</td><td class="event-cell">{deep_entry}</td><td class="event-cell">{yr}</td><td class="event-cell">{subset["Close"].idxmax().strftime("%d-%b")}</td><td class="event-cell">{rt:.2f}%</td></tr>'
                            else: raise ValueError
                        except:
                            html += f'<tr><td class="event-cell">-</td><td class="event-cell">{deep_entry}</td><td class="event-cell">{yr}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td></tr>'
                    
                    html += '</table>'
                    st.markdown(html, unsafe_allow_html=True)

                    # --- एरर फिक्स सेक्शन (Safety First) ---
                    st.markdown("---")
                    f1, f2 = st.columns(2)
                    
                    with f1:
                        # अगर returns खाली है तो एरर न दें
                        if len(returns) > 5:
                            sorted_ret = sorted(returns)
                            t90, t80, t70 = sorted_ret[-2], sorted_ret[-3], sorted_ret[-4]
                            acc_str = f"{t90:.1f}% / {t80:.1f}% / {t70:.1f}%"
                        else:
                            acc_str = "डेटा कम है (Pending)"
                        
                        st.write(f"**Stock:** {inf.get('longName', deep_ticker)}")
                        st.write(f"**Forecast:** {inf.get('targetMeanPrice', 'N/A')}")
                        st.metric("Cycle Accuracy (90/80/70)", acc_str)
                    
                    with f2:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div style="background-color:#00cc66; color:white; text-align:center; font-weight:bold;">FUNDAMENTAL SCORECARD</div>
                            <p>PE: {inf.get('trailingPE', 0):.2f} | ROE: {inf.get('returnOnEquity', 0)*100:.2f}%</p>
                            <p>Debt/Eq: {inf.get('debtToEquity', 0)/100:.2f} | ICR: {inf.get('interestCoverage', 0):.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"सिस्टम अलर्ट: {e}. कृपया सुनिश्चित करें कि तारीख 20-Jan जैसे फॉर्मेट में है।")
                        
