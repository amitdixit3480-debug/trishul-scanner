import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- पेज सेटिंग ---
st.set_page_config(page_title="महाकाल त्रिशूल: सुपर इंडेक्स", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-image: linear-gradient(to right, #800000, #ff4500, #ff8c00); color: white; border: none; font-weight: bold; font-size: 16px; }
    .stDataFrame { border: 2px solid #ff4500; border-radius: 15px; }
    h1 { color: #ff4500; text-align: center; }
    div.stDownloadButton > button { background-color: #28a745 !important; color: white !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱 महाकाल त्रिशूल: Universal Cycle Scanner")

# --- आपकी दी हुई महा-लिस्ट (Pre-loaded) ---
N200_LIST = [
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
    "ZEEL.NS", "ZYDUSLIFE.NS"
]

# स्टॉक लिस्ट को स्ट्रिंग में बदलना
N200_STR = ", ".join(N200_LIST)
N50_STR = "RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, BHARTIARTL.NS, AXISBANK.NS, ITC.NS, LT.NS"

# --- सेशन स्टेट ---
if 'current_list' not in st.session_state:
    st.session_state.current_list = N50_STR

# --- बटन्स ---
st.subheader("🚩 विश्लेषण के लिए सेगमेंट चुनें")
c1, c2 = st.columns(2)
if c1.button("🕉️ NIFTY 50 (Top)"): st.session_state.current_list = N50_STR
if c2.button("🔥 NIFTY 200+ (आपकी महा-लिस्ट)"): st.session_state.current_list = N200_STR

stocks_input = st.text_area("स्टॉक लिस्ट (Search or Edit)", value=st.session_state.current_list, height=150)

# --- साइडबार ---
with st.sidebar:
    st.header("⚙️ महाकाल सेटिंग्स")
    date_range = st.date_input("चक्र की अवधि चुनें", [datetime(2026, 3, 1), datetime(2026, 4, 20)], format="DD/MM/YYYY")
    if len(date_range) == 2:
        s_d, s_m = date_range[0].day, date_range[0].month
        e_d, e_m = date_range[1].day, date_range[1].month
    else: st.stop()
    
    min_acc = st.slider("Accuracy Filter %", 0, 100, 75)
    min_ret = st.slider("Min Return Filter %", 0, 20, 5)

# --- विश्लेषण शुरू ---
if st.button("🚩 महाकाल त्रिशूल विश्लेषण शुरू करें"):
    tickers = [s.strip() for s in stocks_input.split(',') if s.strip()]
    
    with st.spinner(f'{len(tickers)} स्टॉक्स का महा-स्कैन जारी है...'):
        # डेटा डाउनलोड
        all_data = yf.download(tickers, period="12y", interval="1d", progress=False, group_by='ticker')
        results, curr_yr = [], datetime.now().year

        for ticker in tickers:
            try:
                df = all_data[ticker] if len(tickers) > 1 else all_data
                if df.empty: continue
                
                wins, yearly_data = 0, {}
                for yr in range(curr_yr - 10, curr_yr):
                    try:
                        sd, ed = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                        si, ei = df.index.asof(sd), df.index.asof(ed)
                        if si and ei:
                            r = ((df.loc[ei]['Close'] - df.loc[si]['Open']) / df.loc[si]['Open']) * 100
                            yearly_data[str(yr)] = round(r, 2)
                            if r > 0: wins += 1
                    except: continue

                if yearly_data:
                    acc = (wins / len(yearly_data)) * 100
                    avg_r = sum(yearly_data.values()) / len(yearly_data)
                    
                    if acc >= min_acc and avg_r >= min_ret:
                        row = {"Stock": ticker.replace(".NS",""), "Win Rate": f"{int(acc)}%", "Avg Ret": f"{round(avg_r, 2)}%"}
                        row.update(yearly_data)
                        results.append(row)
            except: continue

        if results:
            final_df = pd.DataFrame(results)
            def color_rets(val):
                if isinstance(val, (int, float)):
                    return 'background-color: #c6efce; color: #006100;' if val > 0 else 'background-color: #ffc7ce; color: #9c0006;'
                return ''
            
            st.success(f"🔱 महाकाल कृपा से {len(results)} जैकपॉट मिले!")
            st.dataframe(final_df.style.applymap(color_rets, subset=final_df.columns[3:]).format(precision=2))
            
            csv = final_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 एक्सेल शीट डाउनलोड करें", csv, "Mahakal_Research.csv", "text/csv")
        else:
            st.error("कोई स्टॉक इन फिल्टर्स में नहीं मिला।")
