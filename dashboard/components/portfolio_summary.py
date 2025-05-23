import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from config.config import get_mode
from utils.kraken_wrapper import get_prices, get_live_balances

from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=10_000, key="auto_refresh_summary")


    # Mock snapshot (replace with real file load later)
def render_portfolio_summary(mode=None):
    # Sanitize mode if not passed in
    if mode is None:
        mode = get_mode()

    folder = "json_paper" if mode == "paper" else "json_live"
    portfolio_file = f"data/{folder}/portfolio/portfolio_snapshot.json"

    # === Load snapshot data
    if mode == "paper":
        try:
            with open(portfolio_file) as f:
                snapshot = json.load(f)
        except FileNotFoundError:
            snapshot = {
                "total_value": 0,
                "usd_balance": 0,
                "coins": {}
            }

        prices = get_prices()

        # Recalculate total value using latest prices
        total_value = snapshot.get("usd_balance", 0)
        for coin, info in snapshot.get("coins", {}).items():
            balance = info.get("balance", 0)
            price = prices.get(coin, 0)
            value = round(balance * price, 2)
            info["price"] = price
            info["value"] = value
            total_value += value

        snapshot["total_value"] = round(total_value, 2)

    else:
        balances = get_live_balances()
        prices = get_prices()

        snapshot = {
            "total_value": 0,
            "usd_balance": balances.get("USD", 0),
            "coins": {}
        }

        for coin, amount in balances.items():
            if coin == "USD":
                continue
            price = prices.get(coin, 0)
            value = round(amount * price, 2)
            snapshot["coins"][coin] = {
                "balance": amount,
                "price": price,
                "value": value
            }
            snapshot["total_value"] += value

        snapshot["total_value"] += snapshot["usd_balance"]

    # Mock performance log (replace with calculate_gains later)
    performance_data = {
        "Daily": {"profit": 420.35, "pct": 0.28},
        "Weekly": {"profit": 2750.10, "pct": 1.85},
        "Monthly": {"profit": 8820.45, "pct": 6.30},
        "Yearly": {"profit": 51230.77, "pct": 52.63},
        "Overall": {"profit": 68750.55, "pct": 86.28}
    }

    # === BUBBLE STYLES ===
    st.markdown("""
        <style>
        .bubble-card {
            padding: 20px;
            border-radius: 16px;
            background-color: #f1f3f8;
            box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            text-align: center;
        }
        .bubble-card h4 {
            margin: 0;
            font-size: 22px;
            color: #222;
        }
        .bubble-card p {
            margin: 5px 0 0;
            font-size: 18px;
            color: #555;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## **Portfolio Balances**")

    # === Top 3 Info Cards ===
    col1, col2, col3 = st.columns(3)

    live_prices = get_prices()
    btc_price = live_prices.get("BTC", 0)   

    with col1:
        st.markdown('<div class="bubble-card"><h4>Portfolio Value</h4><p>${:,.2f}</p></div>'.format(snapshot["total_value"]), unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="bubble-card"><h4>Available USD</h4><p>${:,.2f}</p></div>'.format(snapshot["usd_balance"]), unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="bubble-card"><h4>BTC Price</h4><p>${:,.2f}</p></div>'.format(btc_price), unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Coin Holdings")

    coin_labels = []
    coin_values = []

    usd_balance = snapshot.get("usd_balance", 0)
    if usd_balance > 0:
        coin_labels.append("USD")
        coin_values.append(usd_balance)

    for coin, info in snapshot.get("coins", {}).items():
        value = info.get("value", 0)
        if value > 0:
            coin_labels.append(coin)
            coin_values.append(value)

    # === Combined Bubble Section for Pie Chart and Performance ===
    col_left, col_right = st.columns([2, 1])

    with col_left:
        #st.markdown('<div class="bubble-card">', unsafe_allow_html=True)
        st.subheader("📊 Allocation Summary")

        # 🪙 Holdings (text-based)
        st.markdown("**Holdings:**", unsafe_allow_html=True)
        for coin, info in snapshot.get("coins", {}).items():
            balance = info.get("balance", 0)
            value = info.get("value", 0.0)
            if balance > 0:
                st.markdown(f"<p style='margin-bottom:2px;'><strong>{coin}</strong> – ${value:,.2f} ({balance:.4f} {coin})</p>", unsafe_allow_html=True)

        #st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        #st.markdown('<div class="bubble-card">', unsafe_allow_html=True)
        if coin_labels and coin_values and len(coin_labels) == len(coin_values):
            fig = px.pie(
                names=coin_labels,
                values=coin_values,
                title="Portfolio Allocation",
                hole=0.4
            )

            fig.update_layout(height=350, width=350)

            st.plotly_chart(fig, use_container_width=True, key="allocation_pie_chart")
        else:
            st.info("No valid portfolio data available to display chart.")
        #st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    # New row for performance
    st.markdown("### 📈 Performance")

    timeframes = ["Daily", "Weekly", "Monthly", "Yearly"]
    cols = st.columns(len(timeframes))

    for i, timeframe in enumerate(timeframes):
        data = performance_data.get(timeframe, {"profit": 0, "pct": 0})
        profit = data["profit"]
        pct = data["pct"]

        with cols[i]:
            st.metric(
                label=f"{timeframe} Profit",
                value=f"${profit:,.2f}",
                delta=f"{pct:.2f}%",
                delta_color="normal" if profit == 0 else ("inverse" if profit < 0 else "off")
            )
    
    
    # === Strategy Allocation Overview (Mock Display) ===
    st.markdown("---")
    st.markdown("### 🧠 Current Strategies")

    coins = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]
    strategies = ["Core", "5 Min RSI", "1 HR RSI", "Bollinger"]

    # Mock strategy data (replace later with real data)
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
