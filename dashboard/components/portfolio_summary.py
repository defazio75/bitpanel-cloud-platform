import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from utils.config import get_mode
from utils.kraken_wrapper import get_prices, get_live_balances
from utils.firebase_db import (
    load_user_profile,
    load_strategy_allocations,
    load_portfolio_snapshot,
    load_coin_state,
    load_performance_snapshot
)

st_autorefresh(interval=10_000, key="auto_refresh_summary")

def render_portfolio_summary(mode, user_id, token):
    st.title("📊 Portfolio Summary")

    if mode is None:
        mode = get_mode(user_id)

    # === Safely Load Token ===
    if "user" not in st.session_state:
        st.warning("⚠️ Not logged in. Please log in to view portfolio data.")
        return

    token = st.session_state.user.get("token", "")
    snapshot = load_portfolio_snapshot(user_id, token, mode)

    if not snapshot:
        st.warning("No portfolio data found.")
        return

    prices = get_prices(user_id=user_id)
    
    total_value = snapshot.get("usd_balance", 0)
    coin_data = {}

    for coin, info in snapshot.items():
        if coin in ["usd_balance", "total_value", "total_value_usd"]:
            continue  # skip meta fields

        if not isinstance(info, dict):
            continue

        balance = info.get("amount", 0)
        price = prices.get(coin, 0)
        value = round(balance * price, 2)

        coin_data[coin] = {
            "balance": balance,
            "value": value,
            "price": price
        }

        total_value += value

    snapshot["total_value"] = round(total_value, 2)

    # === Header Metrics ===
    st.markdown("## **Portfolio Balances**")
    col1, col2, col3 = st.columns(3)

    btc_price = prices.get("BTC", 0)

    with col1:
        st.markdown(f'<div class="bubble-card"><h4>Portfolio Value</h4><p>${snapshot["total_value"]:,.2f}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="bubble-card"><h4>Available USD</h4><p>${snapshot["usd_balance"]:,.2f}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="bubble-card"><h4>BTC Price</h4><p>${btc_price:,.2f}</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    # === Pie Chart Data ===
    coin_labels = []
    coin_values = []

    if snapshot["usd_balance"] > 0:
        coin_labels.append("USD")
        coin_values.append(snapshot["usd_balance"])

    for coin, info in coin_data.items():
        value = info.get("value", 0)
        if value > 0:
            coin_labels.append(coin)
            coin_values.append(value)

    # === Portfolio Breakdown and Chart ===
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Allocation Summary")
        st.markdown("**Holdings:**")
        for coin, info in coin_data.items():
            balance = info.get("balance", 0)
            value = info.get("value", 0.0)
            if balance > 0:
                st.markdown(f"<p style='margin-bottom:2px;'><strong>{coin}</strong> – ${value:,.2f} ({balance:.4f} {coin})</p>", unsafe_allow_html=True)

    with col_right:
        if coin_labels and coin_values:
            fig = px.pie(
                names=coin_labels,
                values=coin_values,
                title="Portfolio Allocation",
                hole=0.4
            )
            fig.update_layout(height=350, width=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No valid portfolio data available to display chart.")

    st.markdown("---")

    # === Performance Section (To be replaced with real calc) ===
    st.markdown("### 📈 Performance")
    performance_data = {
        "Daily": {"profit": 420.35, "pct": 0.28},
        "Weekly": {"profit": 2750.10, "pct": 1.85},
        "Monthly": {"profit": 8820.45, "pct": 6.30},
        "Yearly": {"profit": 51230.77, "pct": 52.63},
        "Overall": {"profit": 68750.55, "pct": 86.28}
    }

    timeframes = ["Daily", "Weekly", "Monthly", "Yearly"]
    cols = st.columns(len(timeframes))

    for i, tf in enumerate(timeframes):
        data = performance_data[tf]
        st.metric(
            label=f"{tf} Profit",
            value=f"${data['profit']:,.2f}",
            delta=f"{data['pct']:.2f}%",
            delta_color="normal" if data['profit'] == 0 else ("inverse" if data['profit'] < 0 else "off")
        )

    # === Strategy Breakdown (Mock) ===
    st.markdown("---")
    st.markdown("### 🧠 Current Strategies")

    coins = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]
    strategies = ["Core", "5 Min RSI", "1 HR RSI", "Bollinger"]

    mock_data = {
        coin: {
            strategy: {
                "usd": 1000 + i * 250,
                "pct": 25,
                "profit": 50.0 - i * 10,
                "status": "Holding" if i % 2 == 0 else "Waiting"
            }
            for i, strategy in enumerate(strategies)
        }
        for coin in coins
    }

    tab_objs = st.tabs(coins)
    for i, coin in enumerate(coins):
        with tab_objs[i]:
            st.subheader(f"{coin} Strategy Breakdown")
            for strategy in strategies:
                data = mock_data[coin][strategy]
                st.markdown(
                    f"<p style='margin-bottom:6px;'>"
                    f"<strong>{strategy}</strong>: "
                    f"${data['usd']:,} ({data['pct']}%) | "
                    f"Profit: ${data['profit']:.2f} | "
                    f"Status: {data['status']}"
                    f"</p>",
                    unsafe_allow_html=True
                )
