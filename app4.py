import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.set_page_config(page_title="🔱 TRISHUL Time Weapon", layout="wide")

# --- CONFIG ---
CONFIG = [
    {"id": "1sYZoR__O5EQIKdexmnJdRs84gQ_gGPe-osYENtl7YsE", "sheet": "ALL_STOCKS_RAW_DATA"},
    {"id": "15DTT69OOyWSqFOIPIDkNIagcfzdnmcu690AdC0BFR2k", "sheet": "ALL_STOCKS_RAW_DATA2"},
    {"id": "1U1sLZRtkGli-GNAN6cZNGHeOfee8uqSQUJK8K8fhEWQ", "sheet": "ALL_STOCKS_RAW_DATA3"}
]

# --- AUTH ---
@st.cache_resource
def connect_gsheet():
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    return gspread.authorize(creds)

# --- LOAD DATA ---
@st.cache_data(ttl=3600)
def load_data():
    gc = connect_gsheet()
    all_data = []

    for file in CONFIG:
        sh = gc.open_by_key(file["id"]).worksheet(file["sheet"])
        data = sh.get_all_records()
        df = pd.DataFrame(data)
        all_data.append(df)

    master = pd.concat(all_data)
    master["Date"] = pd.to_datetime(master["Date"])
    master = master.sort_values(["Stock Name", "Date"])

    return master

# --- TIME ENGINE ---
def run_time_engine(df):

    results = []

    for stock, data in df.groupby("Stock Name"):
        data = data.sort_values("Date")
        closes = data["Close"].values

        if len(closes) < 2000:
            continue

        best_win = 0
        best_avg = 0
        best_window = 0

        for window in range(10, 46):
            rets = (closes[window:] - closes[:-window]) / closes[:-window] * 100
            if len(rets) < 50:
                continue

            win_rate = (rets > 0).mean() * 100
            avg_ret = rets.mean()

            if win_rate > best_win and avg_ret > best_avg:
                best_win = win_rate
                best_avg = avg_ret
                best_window = window

        if best_win >= 70 and best_avg >= 3:
            score = (best_win * 0.4) + (best_avg * 0.3)
            results.append([stock, best_window, best_win, best_avg, score])

    result_df = pd.DataFrame(results, columns=[
        "Stock", "Best Window (Days)", "Win %", "Avg %", "Score"
    ])

    return result_df.sort_values("Score", ascending=False)

# --- UI ---
st.title("🔱 TRISHUL Time-Cycle Weapon")
st.caption("Pure Statistical Seasonal Edge Engine")

if st.button("🚀 Run Full Scan"):

    with st.spinner("Syncing Google Sheets & Scanning 500 Stocks..."):
        data = load_data()
        result = run_time_engine(data)

    if not result.empty:
        st.success(f"🎯 {len(result)} High Probability Stocks Found")
        st.dataframe(result, use_container_width=True)
    else:
        st.error("❌ No Stocks Met Criteria")
