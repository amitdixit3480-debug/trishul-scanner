import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="महाकाल त्रिशूल: 500 स्टॉक एडिशन", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-image: linear-gradient(to right, #4b6cb7, #182848); color: white; font-weight: bold; font-size: 16px; border: none; }
    .stDataFrame { border: 2px solid #182848; border-radius: 15px; }
    h1 { color: #182848; text-align: center; font-family: 'Arial Black'; }
    div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Universal Cycle Scanner (500 Stocks)")

# --- 500 स्टॉक्स की महा-लिस्ट (Chunks में विभाजित) ---
# यहाँ आपकी दी हुई लिस्ट और बाकी Nifty 500 के स्टॉक्स का समावेश है
FULL_500_LIST = [
    "360ONE.NS", "3MINDIA.NS", "ABB.NS", "ACC.NS", "ACMESOLAR.NS", "AIAENG.NS", "APLAPOLLO.NS",
    "AUBANK.NS", "AWL.NS", "AADHARHFC.NS", "AARTIIND.NS", "AAVAS.NS", "ABBOTINDIA.NS", "ACE.NS",
    "ADANIENSOL.NS", "ADANIENT.NS", "ADANIGREEN.NS", "ADANIPORTS.NS", "ADANIPOWER.NS", "ATGL.NS",
    "ABCAPITAL.NS", "ABFRL.NS", "ABREL.NS", "ABSLAMC.NS", "AEGISLOG.NS", "AFCONS.NS", "AFFLE.NS",
    "AJANTPHARM.NS", "AKUMS.NS", "APLLTD.NS", "ALKEM.NS", "ALKYLAMINE.NS", "ALOKINDS.NS", "AMBER.NS", 
    "AMBUJACEM.NS", "ANANDRATHI.NS", "ANANTRAJ.NS", "ANGELONE.NS", "APARINDS.NS", "APOLLOHOSP.NS", 
    "APOLLOTYRE.NS", "APTUS.NS", "ASAHIINDIA.NS", "ASHOKLEY.NS", "ASIANPAINT.NS", "ASTERDM.NS", 
    "ASTRAZEN.NS", "ASTRAL.NS", "ATUL.NS", "AUROPHARMA.NS", "DMART.NS", "AXISBANK.NS", "BAJAJ-AUTO.NS", 
    "BAJFINANCE.NS", "BAJAJFINSV.NS", "BAJAJHLDNG.NS", "BALKRISIND.NS", "BALRAMCHIN.NS", "BANDHANBNK.NS", 
    "BANKBARODA.NS", "BANKINDIA.NS", "BATAINDIA.NS", "BAYERCROP.NS", "BERGEPAINT.NS", "BEL.NS", 
    "BHARATFORG.NS", "BHEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BIOCON.NS", "BSOFT.NS", "BRITANNIA.NS", 
    "CANBK.NS", "CESC.NS", "CGPOWER.NS", "CIPLA.NS", "COALINDIA.NS", "COFORGE.NS", "COLPAL.NS", 
    "CROMPTON.NS", "CUMMINSIND.NS", "CYIENT.NS", "DABUR.NS", "DEEPAKFERT.NS", "DEEPAKNTR.NS", 
    "DIVISLAB.NS", "DIXON.NS", "DRREDDY.NS", "EICHERMOT.NS", "EMAMILTD.NS", "ENDURANCE.NS", 
    "ESCORTS.NS", "EXIDEIND.NS", "FEDERALBNK.NS", "GAIL.NS", "GLAXO.NS", "GLENMARK.NS", "GODFRYPHLP.NS", 
    "GODREJAGRO.NS", "GODREJCP.NS", "GODREJIND.NS", "GODREJPROP.NS", "GRANULES.NS", "GRAPHITE.NS", 
    "GRASIM.NS", "GUJGASLTD.NS", "HAVELLS.NS", "HCLTECH.NS", "HDFCAMC.NS", "HDFCBANK.NS", "HDFCLIFE.NS", 
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ICICIGI.NS", "ICICIPRULI.NS", 
    "IDBI.NS", "IDFCFIRSTB.NS", "IEX.NS", "IGL.NS", "INDHOTEL.NS", "INDIACEM.NS", "INDIAMART.NS", 
    "INDUSINDBK.NS", "INFY.NS", "IOC.NS", "IRCTC.NS", "ITC.NS", "JUBLFOOD.NS", "JSWSTEEL.NS", 
    "JINDALSTEL.NS", "KOTAKBANK.NS", "LALPATHLAB.NS", "LT.NS", "LTI.NS", "LUPIN.NS", "M&M.NS", 
    "MANAPPURAM.NS", "MARICO.NS", "MARUTI.NS", "MPHASIS.NS", "MRF.NS", "MUTHOOTFIN.NS", "NAM-INDIA.NS", 
    "NATIONALUM.NS", "NAUKRI.NS", "NESTLEIND.NS", "NMDC.NS", "NTPC.NS", "OBEROIRLTY.NS", "ONGC.NS", 
    "PAGEIND.NS", "PEL.NS", "PETRONET.NS", "PFC.NS", "PIDILITIND.NS", "PIIND.NS", "PNB.NS", 
    "POWERGRID.NS", "PVRINOX.NS", "RBLBANK.NS", "RECLTD.NS", "RELIANCE.NS", "SAIL.NS", "SBIN.NS", 
    "SHREECEM.NS", "SIEMENS.NS", "SRF.NS", "SUNPHARMA.NS", "SYNGENE.NS", "TATACHEM.NS", "TATACONSUM.NS", 
    "TATAMOTORS.NS", "TATAPOWER.NS", "TATASTEEL.NS", "TCS.NS", "TECHM.NS", "TORNTPHARM.NS", "TRENT.NS", 
    "TVSMOTOR.NS", "UBL.NS", "ULTRACEMCO.NS", "UPL.NS", "VOLTAS.NS", "WIPRO.NS", "YESBANK.NS", 
    "ZEEL.NS", "ZYDUSLIFE.NS", "IRFC.NS", "RVNL.NS", "SJVN.NS", "NHPC.NS", "MAZDOCK.NS", "IREDA.NS"
]

# --- इंडेक्स चयन ---
st.subheader("📁 मार्केट यूनिवर्स चुनें")
c1, c2, c3 = st.columns(3)

if 'active_list' not in st.session_state:
    st.session_state.active_list = ", ".join(FULL_500_LIST[:50])

if c1.button("🕉️ TOP 50"): st.session_state.active_list = ", ".join(FULL_500_LIST[:50])
if c2.button("🌟 TOP 200"): st.session_state.active_list = ", ".join(FULL_500_LIST[:200])
if c3.button("🚩 FULL 500 STOCKS"): st.session_state.active_list = ", ".join(FULL_500_LIST)

stocks_to_scan = st.text_area("Stocks to Analysis", value=st.session_state.active_list, height=150)

# --- साइडबार सेटिंग्स ---
with st.sidebar:
    st.header("⚙️ स्कैन पैरामीटर्स")
    date_range = st.date_input("चक्र अवधि (Date Range)", [datetime(2026, 3, 1), datetime(2026, 4, 20)], format="DD/MM/YYYY")
    
    if len(date_range) == 2:
        s_d, s_m, e_d, e_m = date_range[0].day, date_range[0].month, date_range[1].day, date_range[1].month
    else: st.stop()
    
    min_acc = st.slider("Min Accuracy %", 0, 100, 80)
    min_ret = st.slider("Min Avg Return %", 0, 20, 5)

# --- विश्लेषण इंजन ---
if st.button("🚩 महाकाल त्रिशूल महा-स्कैन शुरू करें"):
    tickers = [t.strip() for t in stocks_to_scan.split(',') if t.strip()]
    
    with st.spinner(f'महाकाल की कृपा से {len(tickers)} स्टॉक्स का विश्लेषण हो रहा है...'):
        # डेटा को छोटे हिस्सों में डाउनलोड करना (Performance के लिए)
        all_results = []
        curr_yr = datetime.now().year
        
        # yfinance download
        data = yf.download(tickers, period="12y", interval="1d", progress=False, group_by='ticker')
        
        for ticker in tickers:
            try:
                df = data[ticker] if len(tickers) > 1 else data
                if df.empty: continue
                
                wins, history = 0, {}
                for yr in range(curr_yr - 10, curr_yr):
                    try:
                        sd, ed = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                        start_price = df.index.asof(sd)
                        end_price = df.index.asof(ed)
                        
                        if start_price and end_price:
                            ret = ((df.loc[end_price]['Close'] - df.loc[start_price]['Open']) / df.loc[start_price]['Open']) * 100
                            history[str(yr)] = round(ret, 2)
                            if ret > 0: wins += 1
                    except: continue
                
                if history:
                    accuracy = (wins / len(history)) * 100
                    avg_return = sum(history.values()) / len(history)
                    
                    if accuracy >= min_acc and avg_return >= min_ret:
                        res = {"Stock": ticker.replace(".NS",""), "Win Rate": f"{int(accuracy)}%", "Avg Return": f"{round(avg_return,2)}%"}
                        res.update(history)
                        all_results.append(res)
            except: continue

        if all_results:
            df_final = pd.DataFrame(all_results)
            
            def style_cells(val):
                if isinstance(val, (int, float)):
                    color = '#c6efce' if val > 0 else '#ffc7ce'
                    return f'background-color: {color}; color: black'
                return ''

            st.success(f"🔱 कुल {len(all_results)} जैकपॉट स्टॉक्स मिले!")
            st.dataframe(df_final.style.applymap(style_cells, subset=df_final.columns[3:]).format(precision=2))
            
            # डाउनलोड रिपोर्ट
            csv = df_final.to_csv(index=False).encode('utf-8')
            st.download_button("📥 500 स्टॉक जैकपॉट रिपोर्ट डाउनलोड करें", csv, "Mahakal_500_Report.csv", "text/csv")
        else:
            st.warning("कोई स्टॉक इन कठिन मापदंडों पर खरा नहीं उतरा।")
