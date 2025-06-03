import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from utils.config import get_mode
from utils.kraken_wrapper import get_prices, get_live_balances
from utils.firebase_db import load_portfolio_snapshot, load_performance_snapshot, load_coin_state

st_autorefresh(interval=10_000, key="auto_refresh_summary")

def render_portfolio_summary(mode, user_id, token):
    st.title("📊 Portfolio Summary")

    # === Load Portfolio ===
    snapshot = load_portfolio_snapshot(user_id, mode, token)
    if not snapshot:
        st.warning("No portfolio data found.")
        return

    prices = get_prices(user_id=user_id)
    
    # === Portfolio Header ===
    st.subheader("💰 Total Portfolio Value")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Value", f"${snapshot['total_value']:,.2f}")
    col2.metric("USD Balance", f"${snapshot['usd_balance']:,.2f}")
    col3.metric("BTC Price", f"${prices.get('BTC', 0):,.2f}")

    # === Pie Chart ===
    st.subheader("📈 Portfolio Allocation")
    allocation_data = []
    for coin, data in snapshot["coins"].items():
        allocation_data.append({"coin": coin, "value": data["value"]})
    df = px.data.tips()  # placeholder to prevent empty px error
    if allocation_data:
        df = px.data.frame(allocation_data)
        fig = px.pie(df, names="coin", values="value", title="Asset Allocation")
        st.plotly_chart(fig, use_container_width=True)

    # === Performance ===
    st.subheader("📊 Portfolio Performance")
    performance_data = load_performance_snapshot(user_id, mode, token)
    if not performance_data:
        st.info("Performance data not available.")
    else:
        cols = st.columns(5)
        for i, (period, data) in enumerate(performance_data.items()):
            cols[i].metric(
                label=period,
                value=f"${data.get('profit', 0):,.2f}",
                delta=f"{data.get('pct', 0):.2f}%"
            )

    # === Strategy Breakdown ===
    st.subheader("🧠 Current Strategies")
    strategies = ["HODL", "RSI_5MIN", "RSI_1HR", "BOLL"]
    for coin in snapshot["coins"]:
        state = load_coin_state(coin, user_id=user_id, token=token, mode=mode)
        if not state:
            continue

        with st.expander(f"{coin} Strategy Breakdown"):
            for strategy in strategies:
                strat_data = state.get(strategy)
                if not strat_data:
                    continue
                amount = strat_data.get("amount", 0)
                usd_held = strat_data.get("usd_held", 0)
                status = strat_data.get("status", "Unknown")
                profit = strat_data.get("profit", 0)
                total_usd = round(amount * prices.get(coin, 0), 2) + usd_held
                st.write(
                    f"**{strategy}** | Status: `{status}` | Value: `${total_usd:,.2f}` | Profit: `${profit:,.2f}`"
                )
