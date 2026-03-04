import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="महाकाल त्रिशूल: Cycle Master PRO", layout="wide")

# --- CSS: इमेज जैसा लुक (Pink/Yellow/Green) ---
st.markdown("""
    <style>
    .event-header { background-color: #df80ff; color: black; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc; border: 1px solid black; text-align: center; padding: 8px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc; border: 1px solid black; text-align: center; color: red; font-weight: bold; }
    .stat-label { font-weight: bold; background-color: #f2f2f2; border: 1px solid #ddd; padding: 5px; color: black; }
    .stat-val { color: #d35400; font-weight: bold; text-align: right; border: 1px solid #ddd; padding: 5px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(to right, #800000, #ff4500); color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Universal Cycle Scanner & Analyzer")

# --- टैब सिस्टम ---
tab1, tab2 = st.tabs(["🔍 महा-स्कैनर (500 Stocks)", "📊 डीप साइकिल एनालिसिस"])

# ------------------------------------------------------------------
# TAB 1: UNIVERSAL SCANNER
# ------------------------------------------------------------------
with tab1:
    st.subheader("🚩 मार्केट सेगमेंट स्कैन")
    
    # आपकी 500 स्टॉक्स की लिस्ट का छोटा हिस्सा (उदाहरण के लिए)
    DEFAULT_LIST = "VADILALIND.NS, SANGHVIMOV.NS, CHOLAFIN.NS, ITC.NS, NTPC.NS, SBIN.NS, RELIANCE.NS, TCS.NS"
    
    c1, c2 = st.columns([3, 1])
    with c1:
        stocks_input = st.text_area("स्टॉक लिस्ट (कॉमा से अलग करें)", value=DEFAULT_LIST, height=100)
    with c2:
        date_scan = st.date_input("स्कैन अवधि (Date Range)", [datetime(2026, 3, 1), datetime(2026, 5, 20)])
        min_acc = st.slider("Min Accuracy %", 0, 100, 70)

    if st.button("🚩 महा-स्कैन शुरू करें"):
        tickers = [t.strip() for t in stocks_input.split(',') if t.strip()]
        with st.spinner('महाकाल की कृपा से स्कैनिंग जारी है...'):
            try:
                data = yf.download(tickers, period="12y", interval="1d", progress=False, group_by='ticker')
                results = []
                s_d, s_m = date_scan[0].day, date_scan[0].month
                e_d, e_m = date_scan[1].day, date_scan[1].month
                
                for t in tickers:
                    try:
                        df = data[t] if len(tickers) > 1 else data
                        wins, yearly = 0, {}
                        for yr in range(datetime.now().year-10, datetime.now().year):
                            try:
                                sd, ed = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                                si = df.index.asof(sd)
                                ei = df.index.asof(ed)
                                r = ((df.loc[ei]['Close'] - df.loc[si]['Open']) / df.loc[si]['Open']) * 100
                                yearly[str(yr)] = round(r, 2)
                                if r > 0: wins += 1
                            except: continue
                        if yearly:
                            acc = (wins/len(yearly))*100
                            if acc >= min_acc:
                                row = {"Stock": t, "Accuracy": f"{int(acc)}%"}
                                row.update(yearly)
                                results.append(row)
                    except: continue
                if results:
                    st.dataframe(pd.DataFrame(results))
                else:
                    st.warning("कोई स्टॉक फिल्टर में नहीं मिला।")
            except Exception as e:
                st.error(f"स्कैनर एरर: {e}")

# ------------------------------------------------------------------
# TAB 2: DEEP CYCLE ANALYSIS (इमेज जैसा)
# ------------------------------------------------------------------
with tab2:
    st.subheader("📊 स्टॉक डीप डाइव (एक्सेल स्टाइल रिपोर्ट)")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        t_deep = st.text_input("स्टॉक टिकर", "VADILALIND.NS")
    with col_b:
        entry_date = st.text_input("एंट्री डेट (उदा: 20-Jan)", "20-Jan")
    with col_c:
        exit_label = st.text_input("एग्जिट अनुमान", "1st Week of April")

    if st.button("🚩 जेनरेट चक्र रिपोर्ट"):
        try:
            with st.spinner('गहराई से डेटा निकाला जा रहा है...'):
                stock = yf.Ticker(t_deep)
                hist = stock.history(period="max")
                info = stock.info
                
                # --- ऐतिहासिक चक्र टेबल ---
                day, mon_name = entry_date.split('-')
                m_num = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}[mon_name]
                
                html = '<table style="width:100%; border:1px solid black; border-collapse: collapse;">'
                html += '<tr class="event-header"><td>EVENT</td><td>Entry Date</td><td>Year</td><td>Exit/High</td><td>Return (%)</td><td>Weekend</td></tr>'
                
                returns = []
                for i, yr in enumerate(range(datetime.now().year-1, datetime.now().year-11, -1)):
                    try:
                        sd = datetime(yr, m_num, int(day))
                        ed = sd + timedelta(days=75)
                        actual_sd = hist.index[hist.index >= pd.Timestamp(sd)][0]
                        actual_ed = hist.index[hist.index <= pd.Timestamp(ed)][-1]
                        p_start, p_end = hist.loc[actual_sd]['Open'], hist.loc[actual_ed]['Close']
                        ret = ((p_end - p_start) / p_start) * 100
                        returns.append(ret)
                        html += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{entry_date}</td><td class="event-cell">{yr}</td><td class="event-cell">{actual_ed.strftime("%d-%b")}</td><td class="event-cell">{ret:.2f}%</td><td class="event-cell">{"YES" if sd.weekday()>=5 else "NO"}</td></tr>'
                    except:
                        html += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{entry_date}</td><td class="event-cell">{yr}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td><td class="event-cell">-</td></tr>'
                
                html += '</table>'
                st.markdown(html, unsafe_allow_html=True)

                # --- फंडामेंटल स्कोरकार्ड ---
                st.markdown("---")
                f1, f2 = st.columns(2)
                with f1:
                    st.success(f"FORECAST: {info.get('targetMeanPrice', '131')} | SEGMENT: CASH")
                    acc_final = (sum(1 for r in returns if r > 0) / len(returns) * 100) if returns else 0
                    st.metric("Historical Accuracy", f"{int(acc_final)}%")
                
                with f2:
                    # ICR कैलकुलेशन
                    try:
                        icr = stock.financials.loc['EBIT'].iloc[0] / abs(stock.financials.loc['Interest Expense'].iloc[0])
                    except: icr = 0
                    
                    st.markdown(f"""
                    <table style="width:100%; border:2px solid #00cc66; border-collapse: collapse;">
                        <tr style="background-color:#00cc66; color:white;"><td colspan="2" style="padding:10px; font-weight:bold; text-align:center;">🔱 FUNDAMENTAL SCORECARD</td></tr>
                        <tr><td class="stat-label">P/E Ratio</td><td class="stat-val">{info.get('trailingPE',0):.2f}</td></tr>
                        <tr><td class="stat-label">ROE (%)</td><td class="stat-val">{info.get('returnOnEquity',0)*100:.2f}%</td></tr>
                        <tr><td class="stat-label">Debt to Equity</td><td class="stat-val">{info.get('debtToEquity',0)/100:.2f}</td></tr>
                        <tr><td class="stat-label">Int. Coverage</td><td class="stat-val">{icr:.2f}</td></tr>
                        <tr><td class="stat-label">Industry PE</td><td class="stat-val">{info.get('forwardPE','N/A')}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"डीप एनालिसिस एरर: {e}")
                
