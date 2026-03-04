import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- 1. पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="महाकाल त्रिशूल 3.0", layout="wide")

# --- 2. CSS: विजुअल फिक्स (Pink Header & Yellow Cells) ---
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .event-table { width: 100%; border-collapse: collapse; border: 2px solid black; }
    .event-header { background-color: #df80ff !important; color: black; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc !important; border: 1px solid black; text-align: center; padding: 10px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc !important; border: 1px solid black; text-align: center; color: red !important; font-weight: bold; }
    .stat-box { border: 2px solid #00cc66; border-radius: 10px; padding: 15px; background-color: white; }
    .stat-label { font-weight: bold; color: #333; }
    .stat-val { color: #d35400; font-weight: bold; float: right; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Cycle Master (Fixed)")

# --- 3. टैब सिस्टम (Simple & Clean) ---
tab1, tab2 = st.tabs(["🔍 महा-स्कैनर (500 Stocks)", "📊 डीप एनालिसिस (Excel Style)"])

# --- 4. TAB 1: महा-स्कैनर ---
with tab1:
    st.subheader("🚩 सेक्टर स्कैनिंग")
    # स्टॉक लिस्ट (आप इसे बढ़ा सकते हैं)
    STOCKS = "VADILALIND.NS, SANGHVIMOV.NS, CHOLAFIN.NS, ITC.NS, RELIANCE.NS, SBIN.NS, TCS.NS"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        input_list = st.text_area("स्टॉक लिस्ट डालें:", value=STOCKS, height=100)
    with col2:
        scan_range = st.date_input("अवधि चुनें", [datetime(2026, 3, 1), datetime(2026, 4, 30)])
        min_accuracy = st.slider("Min Accuracy %", 0, 100, 70)

    if st.button("🚩 स्कैन शुरू करें"):
        tickers = [t.strip().upper() for t in input_list.split(',') if t.strip()]
        try:
            with st.spinner('स्कैन हो रहा है...'):
                raw_data = yf.download(tickers, period="15y", interval="1d", progress=False, group_by='ticker')
                scan_results = []
                s_d, s_m = scan_range[0].day, scan_range[0].month
                e_d, e_m = scan_range[1].day, scan_range[1].month

                for t in tickers:
                    try:
                        df = raw_data[t] if len(tickers) > 1 else raw_data
                        wins, yearly_ret = 0, {}
                        for yr in range(datetime.now().year-10, datetime.now().year):
                            try:
                                sd, ed = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                                si = df.index.asof(sd)
                                ei = df.index.asof(ed)
                                r = ((df.loc[ei]['Close'] - df.loc[si]['Open']) / df.loc[si]['Open']) * 100
                                yearly_ret[str(yr)] = round(r, 2)
                                if r > 0: wins += 1
                            except: continue
                        if yearly_ret:
                            acc = (wins/len(yearly_ret))*100
                            if acc >= min_accuracy:
                                res = {"Stock": t, "Win%": f"{int(acc)}%"}
                                res.update(yearly_ret)
                                scan_results.append(res)
                    except: continue
                st.dataframe(pd.DataFrame(scan_results))
        except Exception as e:
            st.error(f"Scanner Error: {e}")

# --- 5. TAB 2: डीप एनालिसिस (इमेज के अनुसार) ---
with tab2:
    st.subheader("📊 स्टॉक डीप डाइव रिपोर्ट")
    c1, c2, c3 = st.columns(3)
    with c1:
        deep_ticker = st.text_input("स्टॉक टिकर (e.g. VADILALIND.NS)", "VADILALIND.NS").upper()
    with c2:
        deep_entry = st.text_input("एंट्री तारीख (DD-Mon)", "20-Jan")
    with c3:
        deep_exit = st.text_input("एग्जिट अनुमान", "30-Apr")

    if st.button("🚩 डीप रिपोर्ट जनरेट करें"):
        try:
            with st.spinner('इतिहास खोजा जा रहा है...'):
                s_obj = yf.Ticker(deep_ticker)
                h_data = s_obj.history(period="15y")
                inf = s_obj.info
                
                day, mon = deep_entry.split('-')
                m_idx = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}[mon]
                
                # टेबल की शुरुआत
                html_code = '<table class="event-table"><tr class="event-header"><td>EVENT</td><td>Entry</td><td>Year</td><td>Exit Date</td><td>Return (%)</td><td>Status</td></tr>'
                
                re_list = []
                for i, yr in enumerate(range(datetime.now().year-1, datetime.now().year-11, -1)):
                    try:
                        sd = datetime(yr, m_idx, int(day))
                        ed = sd + timedelta(days=90)
                        
                        # मार्केट हॉलिडे हैंडलिंग (Fuzzy matching)
                        a_sd = h_data.index[h_data.index >= pd.Timestamp(sd)][0]
                        a_ed = h_data.index[h_data.index <= pd.Timestamp(ed)][-1]
                        
                        ps, pe = h_data.loc[a_sd]['Open'], h_data.loc[a_ed]['Close']
                        rt = ((pe - ps) / ps) * 100
                        re_list.append(rt)
                        
                        html_code += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{deep_entry}</td><td class="event-cell">{yr}</td><td class="event-cell">{a_ed.strftime("%d-%b")}</td><td class="event-cell">{rt:.2f}%</td><td class="event-cell">OK</td></tr>'
                    except:
                        html_code += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{deep_entry}</td><td class="event-cell">{yr}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td><td class="event-cell">-</td></tr>'
                
                html_code += '</table>'
                st.markdown(html_code, unsafe_allow_html=True)
                
                # फंडामेंटल स्कोरकार्ड
                st.markdown("---")
                f_left, f_right = st.columns(2)
                with f_left:
                    st.metric("Cycle Accuracy", f"{(sum(1 for x in re_list if x > 0)/len(re_list)*100 if re_list else 0):.0f}%")
                    st.info(f"FORECAST: {inf.get('targetMeanPrice', 'N/A')} | SEGMENT: CASH")
                
                with f_right:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div style="background-color:#00cc66; color:white; text-align:center; padding:5px; font-weight:bold;">FUNDAMENTAL SCORECARD</div>
                        <p><span class="stat-label">P/E Ratio:</span> <span class="stat-val">{inf.get('trailingPE', 0):.2f}</span></p>
                        <p><span class="stat-label">ROE (%):</span> <span class="stat-val">{inf.get('returnOnEquity', 0)*100:.2f}%</span></p>
                        <p><span class="stat-label">Debt/Equity:</span> <span class="stat-val">{inf.get('debtToEquity', 0)/100:.2f}</span></p>
                        <p><span class="stat-label">Industry PE:</span> <span class="stat-val">{inf.get('forwardPE', 'N/A')}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as ex:
            st.error(f"Deep Analysis Error: {ex}. Check input format.")
                
