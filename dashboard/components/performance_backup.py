import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime


def load_portfolio_history(mode="paper"):
    history_dir = f"data/json_{mode}/portfolio/history"
    data = []

    if not os.path.exists(history_dir):
        return pd.DataFrame()

    for filename in sorted(os.listdir(history_dir)):
        if filename.endswith(".json"):
            try:
                path = os.path.join(history_dir, filename)
                with open(path, "r") as f:
                    snapshot = json.load(f)
                    date_str = snapshot.get("date") or filename.replace(".json", "")
                    value = snapshot.get("total_value", None)

                    if date_str and value is not None:
                        data.append({"date": pd.to_datetime(date_str), "value": value})
            except Exception as e:
                st.warning(f"⚠️ Failed to load {filename}: {e}")

    df = pd.DataFrame(data)
    return df.sort_values("date") if not df.empty else df


def render():

    from config.config import get_mode
    mode = get_mode()
    df = load_portfolio_history(mode)

    if df.empty:
        st.warning("No historical performance data available yet.")
        return

    # === Portfolio Performance Section ===
    st.markdown("### 📈 Total Portfolio Performance")

    latest = df["value"].iloc[-1]
    prev_day = df["value"].iloc[-2] if len(df) >= 2 else latest
    prev_week = df["value"].iloc[-8] if len(df) >= 8 else prev_day
    prev_month = df["value"].iloc[-30] if len(df) >= 30 else prev_week
    first = df["value"].iloc[0]

    def calc_metrics(current, past):
        change = current - past
        pct = (change / past) * 100 if past > 0 else 0
        return f"{pct:.2f}%", f"${change:,.2f}"

    daily_pct, daily_amt = calc_metrics(latest, prev_day)
    weekly_pct, weekly_amt = calc_metrics(latest, prev_week)
    monthly_pct, monthly_amt = calc_metrics(latest, prev_month)
    overall_pct, overall_amt = calc_metrics(latest, first)

    top_row = st.columns(2)
    bottom_row = st.columns(2)

    top_row[0].metric("📆 Daily Return", daily_pct, daily_amt)
    top_row[1].metric("📈 Weekly Return", weekly_pct, weekly_amt)
    bottom_row[0].metric("📅 Monthly Return", monthly_pct, monthly_amt)
    bottom_row[1].metric("💼 Overall Return", overall_pct, overall_amt)

    # === Coin-Specific Returns (replaced with bar chart)
    st.divider()
    st.markdown("### 🪙 Coin Performance Comparison")

    coin_options = ["BTC", "ETH", "SOL", "XRP", "DOT", "LINK"]
    selected_coin = st.selectbox("Select a coin", coin_options)
    timeframe = st.radio("Select timeframe", ["Daily", "Weekly", "Monthly", "Overall"], horizontal=True)

    if not df.empty and "coins" in df.columns:
        coin_data = []
        for i, row in df.iterrows():
            coins = row.get("coins", {})
            if selected_coin in coins:
                coin_value = coins[selected_coin].get("value", 0)
                coin_data.append({"date": row["date"], "value": coin_value})

        coin_df = pd.DataFrame(coin_data)
        if not coin_df.empty:
            latest = coin_df["value"].iloc[-1]
            if timeframe == "Daily":
                compare = coin_df["value"].iloc[-2] if len(coin_df) >= 2 else latest
            elif timeframe == "Weekly":
                compare = coin_df["value"].iloc[-8] if len(coin_df) >= 8 else latest
            elif timeframe == "Monthly":
                compare = coin_df["value"].iloc[-30] if len(coin_df) >= 30 else latest
            else:
                compare = coin_df["value"].iloc[0]

            coin_return = ((latest - compare) / compare) * 100 if compare > 0 else 0

            # BitPanel strategy return (same logic)
            port_latest = df["value"].iloc[-1]
            if timeframe == "Daily":
                port_compare = df["value"].iloc[-2] if len(df) >= 2 else port_latest
            elif timeframe == "Weekly":
                port_compare = df["value"].iloc[-8] if len(df) >= 8 else port_latest
            elif timeframe == "Monthly":
                port_compare = df["value"].iloc[-30] if len(df) >= 30 else port_latest
            else:
                port_compare = df["value"].iloc[0]

            panel_return = ((port_latest - port_compare) / port_compare) * 100 if port_compare > 0 else 0

            perf_df = pd.DataFrame({
                "Metric": ["Market", "BitPanel"],
                "Return %": [coin_return, panel_return]
            })

            bar_chart = alt.Chart(perf_df).mark_bar().encode(
                x=alt.X("Metric:N", title=""),
                y=alt.Y("Return %:Q", title="Return %"),
                color=alt.Color("Metric:N", scale=alt.Scale(range=['#FF6B6B', '#4CAF50']))
            ).properties(
                width=400,
                height=300,
                title=f"{selected_coin} - {timeframe} Return Comparison"
            )

            st.altair_chart(bar_chart, use_container_width=True)
        else:
            st.info(f"No data available for {selected_coin}.")

    st.success("✅ Live performance data loaded.")
