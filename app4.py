import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल: Ultimate Cycle Master", layout="wide")

# --- CSS: इमेज जैसा कलर और फॉन्ट ---
st.markdown("""
    <style>
    .event-header { background-color: #df80ff !important; color: black !important; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc !important; border: 1px solid black; text-align: center; padding: 8px; font-weight: bold; color: black; }
    .fail-cell { background-color: #ffcccc !important; border: 1px solid black; text-align: center; color: red !important; font-weight: bold; }
    .low-broken-cell { background-color: #ffffcc; border: 1px solid black; color: red; font-weight: bold; text-align: center; }
    .stat-label { font-weight: bold; background-color: #f2f2f2; border: 1px solid #ddd; padding: 8px; color: black; }
    .stat-val { color: #d35400; font-weight: bold; text-align: right; border: 1px solid #ddd; padding: 8px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(to right, #b22222, #ff4500); color: white; font-weight: bold; }
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
    DEFAULT_LIST = "RELIANCE.NS, TCS.NS, INFY.NS, ITC.NS, NTPC.NS, SBIN.NS, VADILALIND.NS, SANGHVIMOV.NS, CHOLAFIN.NS"
    
    c1, c2 = st.columns([3, 1])
    with c1:
        stocks_input = st.text_area("स्टॉक लिस्ट", value=DEFAULT_LIST, height=100)
    with c2:
        date_scan = st.date_input("स्कैन चक्र", [datetime(2026, 3, 1), datetime(2026, 5, 20)])
        min_acc = st.slider("Min Accuracy %", 0, 100, 70)

    if st.button("🚩 महा-स्कैन शुरू करें"):
        tickers = [t.strip().upper() for t in stocks_input.split(',') if t.strip()]
        with st.spinner('डेटा एनालिसिस जारी है...'):
            try:
                # बल्क डेटा डाउनलोड
                data = yf.download(tickers, period="12y", interval="1d", progress=False, group_by='ticker')
                results = []
                s_d, s_m = date_scan[0].day, date_scan[0].month
                e_d, e_m = date_scan[1].day, date_scan[1].month
                
                for t in tickers:
                    try:
                        df = data[t] if len(tickers) > 1 else data
                        if df.empty: continue
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
                st.dataframe(pd.DataFrame(results))
            except Exception as e:
                st.error(f"Error: {e}")

# ------------------------------------------------------------------
# TAB 2: DEEP CYCLE ANALYSIS
# ------------------------------------------------------------------
with tab2:
    st.subheader("📊 स्टॉक डीप डाइव (एक्सेल स्टाइल रिपोर्ट)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        t_deep = st.text_input("स्टॉक टिकर (उदा: ITC.NS)", "ITC.NS").upper()
    with col_b:
        entry_date_str = st.text_input("एंट्री डेट (DD-Mon)", "20-Jan")
    with col_c:
        exit_label = st.text_input("एग्जिट अनुमान", "30-Apr")

    if st.button("🚩 जेनरेट चक्र रिपोर्ट"):
        try:
            with st.spinner('महाकाल की कृपा से इतिहास खोजा जा रहा है...'):
                stock_obj = yf.Ticker(t_deep)
                # 'max' की जगह '15y' ताकि डेटा जल्दी लोड हो
                hist = stock_obj.history(period="15y")
                info = stock_obj.info
                
                day, mon_name = entry_date_str.split('-')
                m_num = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}[mon_name]
                
                html = '<table style="width:100%; border:1px solid black; border-collapse: collapse;">'
                html += '<tr class="event-header"><td>EVENT</td><td>Entry Date</td><td>Year</td><td>Exit/High</td><td>Return (%)</td><td>Low Broken</td></tr>'
                
                returns_list = []
                for i, yr in enumerate(range(datetime.now().year-1, datetime.now().year-11, -1)):
                    try:
                        sd = datetime(yr, m_num, int(day))
                        # इमेज के अनुसार चक्र की लंबाई (लगभग 90-100 दिन)
                        ed_target = sd + timedelta(days=100)
                        
                        # मार्केट हॉलिडे हैंडलिंग
                        actual_sd = hist.index[hist.index >= pd.Timestamp(sd)][0]
                        actual_ed = hist.index[hist.index <= pd.Timestamp(ed_target)][-1]
                        
                        p_start = hist.loc[actual_sd]['Open']
                        p_end = hist.loc[actual_ed]['Close']
                        
                        # Low Broken Logic: क्या चक्र के दौरान भाव एंट्री वाले 'Low' के नीचे गया?
                        cycle_data = hist.loc[actual_sd:actual_ed]
                        entry_low = hist.loc[actual_sd]['Low']
                        min_low_in_cycle = cycle_data['Low'].min()
                        low_broken = "YES" if min_low_in_cycle < entry_low else "NO"
                        low_val = round(((entry_low - min_low_in_cycle)/entry_low)*100, 2) if low_broken == "YES" else "NO"

                        ret = ((p_end - p_start) / p_start) * 100
                        returns_list.append(ret)
                        
                        html += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{entry_date_str}</td><td class="event-cell">{yr}</td><td class="event-cell">{actual_ed.strftime("%d-%b")}</td><td class="event-cell">{ret:.2f}%</td><td class="low-broken-cell">{low_val}</td></tr>'
                    except:
                        html += f'<tr><td class="event-cell">{i+1}</td><td class="event-cell">{entry_date_str}</td><td class="event-cell">{yr}</td><td class="fail-cell">FAIL</td><td class="fail-cell">FAIL</td><td class="event-cell">-</td></tr>'
                
                html += '</table>'
                st.markdown(html, unsafe_allow_html=True)

                # --- फंडामेंटल स्कोरकार्ड (मजबूत डेटा) ---
                st.markdown("---")
                f1, f2 = st.columns(2)
                with f1:
                    st.success(f"FORECAST: {info.get('targetMeanPrice', 'N/A')} | SEGMENT: CASH")
                    acc_val = (sum(1 for r in returns_list if r > 0) / len(returns_list) * 100) if returns_list else 0
                    st.metric("Cycle Accuracy", f"{int(acc_val)}%")
                
                with f2:
                    # ROE और Debt/Equity फिक्स
                    roe = info.get('returnOnEquity', 0) * 100
                    de = info.get('debtToEquity', 0)
                    if de > 10: de = de / 100 # yfinance scale fix
                    
                    st.markdown(f"""
                    <table style="width:100%; border:2px solid #00cc66; border-collapse: collapse;">
                        <tr style="background-color:#00cc66; color:white;"><td colspan="2" style="padding:10px; font-weight:bold; text-align:center;">🔱 FUNDAMENTAL SCORECARD</td></tr>
                        <tr><td class="stat-label">P/E Ratio</td><td class="stat-val">{info.get('trailingPE',0):.2f}</td></tr>
                        <tr><td class="stat-label">ROE (%)</td><td class="stat-val">{roe:.2f}%</td></tr>
                        <tr><td class="stat-label">Debt to Equity</td><td class="stat-val">{de:.2f}</td></tr>
                        <tr><td class="stat-label">Industry PE</td><td class="stat-val">{info.get('forwardPE','N/A')}</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}. Check Ticker format (e.g. ITC.NS)")
                    
