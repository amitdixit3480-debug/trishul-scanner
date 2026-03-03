import os
import sys
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
os.environ['STREAMLIT_GATHER_USAGE_STATS'] = 'false'

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Trishul Ultimate Scanner", layout="wide")

# CSS for better UI
st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .bull-card { border-left: 10px solid #166534; background-color: #f0fdf4; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .bear-card { border-left: 10px solid #991b1b; background-color: #fef2f2; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    .trishul-table { width: 100%; border-collapse: collapse; font-size: 12px; }
    .trishul-table th { background-color: #334155; color: white; padding: 8px; }
    .trishul-table td { border: 1px solid #cbd5e1; text-align: center; padding: 6px; font-weight: bold; }
    .pos { color: #166534; background-color: #dcfce7; }
    .neg { color: #991b1b; background-color: #fee2e2; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔱Trishul🔱: Ultimate Date-to-Date Scanner")

# Nifty 50 List
nifty50_list = "ADANIENT.NS, ADANIPORTS.NS, APOLLOHOSP.NS, ASIANPAINT.NS, AXISBANK.NS, BAJAJ-AUTO.NS, BAJFINANCE.NS, BAJAJFINSV.NS, BPCL.NS, BHARTIARTL.NS, BRITANNIA.NS, CIPLA.NS, COALINDIA.NS, DIVISLAB.NS, DRREDDY.NS, EICHERMOT.NS, GRASIM.NS, HCLTECH.NS, HDFCBANK.NS, HDFCLIFE.NS, HEROMOTOCO.NS, HINDALCO.NS, HINDUNILVR.NS, ICICIBANK.NS, ITC.NS, INDUSINDBK.NS, INFY.NS, JSWSTEEL.NS, KOTAKBANK.NS, LTIM.NS, LT.NS, M&M.NS, MARUTI.NS, NTPC.NS, NESTLEIND.NS, ONGC.NS, POWERGRID.NS, RELIANCE.NS, SBILIFE.NS, SBIN.NS, SUNPHARMA.NS, TCS.NS, TATACONSUM.NS, TATAMOTORS.NS, TATASTEEL.NS, TECHM.NS, TITAN.NS, ULTRACEMCO.NS, WIPRO.NS"

with st.sidebar:
    st.header("🔱 Scanner Config")
    c1, c2 = st.columns(2)
    with c1:
        s_d, s_m = st.number_input("Start Day", 1, 31, 1), st.number_input("Start Month", 1, 12, 3)
    with c2:
        e_d, e_m = st.number_input("End Day", 1, 31, 20), st.number_input("End Month", 1, 12, 4)
    
    min_acc = st.slider("Min Accuracy (%)", 50, 100, 70)
    if st.button("🎯 Load NIFTY 50"): st.session_state.stocks = nifty50_list
    user_stocks = st.text_area("Stocks List", value=st.session_state.get('stocks', "RELIANCE.NS, TCS.NS"), height=150)
    run_btn = st.button("🚀 Analyze Strategy")

def display_results(data, title, css_class):
    if not data: return
    st.markdown(f"<div class='{css_class}'><h2>{title}</h2></div>", unsafe_allow_html=True)
    df = pd.DataFrame(data)
    # Reorder columns to show Avg Return next to Win Rate
    cols = ['Stock', 'WR', 'Avg_Ret'] + [str(y) for y in range(datetime.now().year-10, datetime.now().year)]
    df = df[cols]
    
    html = '<table class="trishul-table"><tr>'
    for col in df.columns: html += f'<th>{col}</th>'
    html += '</tr>'
    
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = row[col]
            if col == 'Stock' or col == 'WR' or col == 'Avg_Ret':
                html += f'<td>{val}{"%" if col != "Stock" else ""}</td>'
            else:
                c = "pos" if val > 0 else "neg"
                html += f'<td class="{c}">{val}%</td>'
        html += '</tr>'
    st.write(html + '</table>', unsafe_allow_html=True)

if run_btn:
    all_bulls, all_bears = [], []
    curr_yr = datetime.now().year
    prog = st.progress(0)
    s_list = [s.strip() for s in user_stocks.split(',')]
    
    for i, ticker in enumerate(s_list):
        try:
            df = yf.download(ticker, period="11y", progress=False, auto_adjust=True)
            if df.empty: continue
            
            res = {'Stock': ticker.replace('.NS', ''), 'Wins': 0, 'Losses': 0, 'Returns': []}
            for yr in range(curr_yr - 10, curr_yr):
                try:
                    sd, ed = datetime(yr, s_m, s_d), datetime(yr, e_m, e_d)
                    si = df.index.get_indexer([sd], method='ffill')[0]
                    ei = df.index.get_indexer([ed], method='ffill')[0]
                    if si != -1 and ei != -1:
                        ret = ((float(df.iloc[ei]['Close']) - float(df.iloc[si]['Open'])) / float(df.iloc[si]['Open'])) * 100
                        res[str(yr)] = round(ret, 2)
                        res['Returns'].append(ret)
                        if ret > 0: res['Wins'] += 1
                        else: res['Losses'] += 1
                except: continue
            
            if res['Returns']:
                avg_ret = round(sum(res['Returns']) / len(res['Returns']), 2)
                res['Avg_Ret'] = avg_ret
                bull_rate = int((res['Wins'] / len(res['Returns'])) * 100)
                bear_rate = int((res['Losses'] / len(res['Returns'])) * 100)
                
                if bull_rate >= min_acc:
                    res['WR'] = bull_rate
                    all_bulls.append(res)
                elif bear_rate >= min_acc:
                    res['WR'] = bear_rate
                    all_bears.append(res)
        except: continue
        prog.progress((i + 1) / len(s_list))
    
    prog.empty()
    display_results(sorted(all_bulls, key=lambda x: x['WR'], reverse=True), "📈 Bullish Opportunity (बाय सेटअप)", "bull-card")
    display_results(sorted(all_bears, key=lambda x: x['WR'], reverse=True), "📉 Bearish Opportunity (सेल सेटअप)", "bear-card")

