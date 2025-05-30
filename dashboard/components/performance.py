import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from utils.config import get_mode
from utils.kraken_wrapper import get_prices
from utils.firebase_db import list_firebase_files, load_firebase_json

# === Load snapshots into DataFrame ===
def load_performance_data(user_id, mode):
    file_keys = list_firebase_files("performance/history", mode, user_id)
    snapshots = []

    for key in sorted(file_keys):
        data = load_firebase_json(key.replace(".json", ""), mode, user_id, subfolder="performance/history")
        date = key.replace(".json", "")
        total_value = data.get("total_value", 0.0)
        coins = data.get("coins", {})
        snapshot = {
            "date": date,
            "total_value": total_value,
            **{coin: coins[coin].get("usd", 0.0) for coin in coins}
        }
        snapshots.append(snapshot)

    df = pd.DataFrame(snapshots)
    if df.empty:
        return df
    if "total_value" not in df.columns:
        df["total_value"] = 0.0
    return df

# === Simulate HODL performance (BTC only for now) ===
def simulate_hodl(df):
    if "BTC" not in df.columns or df.empty:
        df["hodl_value"] = df.get("total_value", 0)
        return df
    start_btc = df.iloc[0]["BTC"] / get_prices()["BTC"]
    hodl_values = df["date"].apply(lambda d: start_btc * get_prices()["BTC"])
    df["hodl_value"] = hodl_values
    return df

# === Plot line chart of Portfolio vs HODL ===
def plot_line_chart(df):
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    fig, ax = plt.subplots()
    ax.plot(df["date"], df["total_value"], label="BitPanel Portfolio")
    ax.plot(df["date"], df["hodl_value"], label="Buy & Hold BTC", linestyle="--")
    ax.set_ylabel("Portfolio Value (USD)")
    ax.set_xlabel("Date")
    ax.set_title("BitPanel vs Buy & Hold")
    ax.legend()
    st.pyplot(fig)

# === Display per-coin ROI comparison ===
def show_coin_performance(df):
    if df.empty or df.shape[0] < 2:
        return

    latest = df.iloc[-1]
    first = df.iloc[0]
    coins = [c for c in df.columns if c not in ["date", "total_value", "hodl_value"]]

    st.subheader("📊 Coin Strategy ROI vs Market")
    for coin in coins:
        start = first[coin]
        end = latest[coin]
        if start == 0:
            continue
        roi = ((end - start) / start) * 100
        market_price = get_prices().get(coin, 0)
        market_start = start / market_price if market_price else 0
        market_end = market_start * market_price if market_price else 0
        market_roi = ((market_end - start) / start) * 100

        col1, col2 = st.columns([3, 1])
        col1.write(f"**{coin}**")
        col1.progress(min(max(int(roi), 0), 100))
        col2.write(f"🟢 Bot: {roi:.2f}%\n⚪ Market: {market_roi:.2f}%")

# === Main Render Function ===
def render(mode=None, user_id=None):
    st.title("📈 Portfolio Performance")

    if mode is None:
        mode = get_mode(user_id)

    df = load_performance_data(user_id, mode)

    if df.empty:
        st.warning("No portfolio history found. Start running your strategies to build performance data.")
    else:
        df = simulate_hodl(df)
        plot_line_chart(df)
        show_coin_performance(df)
        st.caption("Note: Strategy values include realized and unrealized gains. Market benchmark is BTC-only for now.")
