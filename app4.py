import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल: Cycle Master PRO", layout="wide")

# --- CSS: इमेज जैसा लुक (Pink/Yellow/Green) ---
st.markdown("""
    <style>
    .event-header { background-color: #df80ff; color: black; font-weight: bold; text-align: center; border: 1px solid black; }
    .event-cell { background-color: #ffffcc; border: 1px solid black; text-align: center; padding: 8px; font-weight: bold; }
    .fail-cell { background-color: #ffcccc; border: 1px solid black; text-align: center; color: red; font-weight: bold; }
    .stat-label { font-weight: bold; background-color: #f2f2f2; border: 1px solid #ddd; padding: 5px; }
    .stat-val { color: #d35400; font-weight: bold; text-align: right; border: 1px solid #ddd; padding: 5px; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(to right, #800000, #ff4500); color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Universal Cycle Scanner & Analyzer")

# --- टैब सिस्टम: स्कैनर और डीप एनालिसिस ---
tab1, tab2 = st.tabs(["🔍 महा-स्कैनर (500 Stocks)", "📊 डीप साइकिल एनालिसिस"])

# ------------------------------------------------------------------
# TAB 1: UNIVERSAL SCANNER (पुराना बेस)
# ------------------------------------------------------------------
with tab1:
    st.subheader("🚩 मार्केट सेगमेंट स्कैन")
    
    FULL_500 = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "VADILALIND.NS", "SANGHVIMOV.NS", "CHOLAFIN.NS", "ITC.NS", "NTPC.NS", "SBIN.NS", "ICICIBANK.NS", "HDFCBANK.NS"] # यहाँ आप अपनी 500 की लिस्ट डालें
    
    c1, c2 = st.columns([3, 1])
    with c1:
        stocks_input = st.text_area("स्टॉक लिस्ट (Search or Edit)", value=", ".join(FULL_500), height=100)
    with c2:
        date_scan = st.date_input("स्कैन अवधि", [datetime(2026, 3, 1), datetime(2026, 5, 20)])
        min_acc = st.slider("Min Accuracy %", 0, 100, 70)

    if st.button("🚩 महा-स्कैन शुरू करें"):
        tickers = [t.strip() for t in stocks_input.split(',') if t.strip()]
        with st.spinner('स्कैनिंग जारी है...'):
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
            st.dataframe(pd.DataFrame(results))

# ------------------------------------------------------------------
# TAB 2: DEEP CYCLE ANALYSIS (इमेज जैसा सेम टू सेम)
# ------------------------------------------------------------------
with tab2:
    st.subheader("📊 स्टॉक डीप डाइव (Excel Style Report)")
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        t_deep = st.text_input("स्टॉक का नाम", "VADILALIND.NS")
    with col_b:
        entry_date = st.text_input("एंट्री डेट (DD-Mon)", "20-Jan")
    with col_c:
        exit_label = st.text_input("एग्जिट अनुमान", "1st Week of April")

    if st.button("🚩 जेनरेट चक्र रिपोर्ट"):
        try:
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
                    p_start, p_end = hist.loc
            
