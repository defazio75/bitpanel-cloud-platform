import sys
import os
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from utils.kraken_wrapper import get_prices, get_live_balances
from utils.config import get_mode
from utils.firebase_db import (
    load_coin_state,
    save_coin_state,
    load_portfolio_snapshot
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bots")))
from utils.trade_simulator import simulate_trade
from utils.trade_executor import execute_trade

def render(user_id, token, mode):
    if not token and "token" in st.session_state:
        token = st.session_state.token

    st.title("🎯 Coin Allocation")
    if mode is None:
        mode = get_mode(user_id)

    st.caption(f"🛠 Mode: **{mode.upper()}**")

    snapshot = load_portfolio_snapshot(user_id, token, mode)
    prices = get_prices(user_id=user_id)

    usd_balance = snapshot.get("usd_balance", 0)
    total_value = usd_balance
    coins = {}

    for coin, info in snapshot.get("coins", {}).items():
        balance = info.get("balance", 0)
        price = prices.get(coin, 0)
        usd_value = round(balance * price, 2)
        total_value += usd_value
        coins[coin] = {
            "balance": balance,
            "usd": usd_value,
            "price": price
        }

    st.metric("💼 Total Portfolio Value", f"${total_value:,.2f}")
    st.metric("💰 Available USD", f"${usd_balance:,.2f}")

    SUPPORTED_COINS = ["BTC", "ETH", "SOL", "XRP", "LINK", "DOT"]
    for coin in SUPPORTED_COINS:
        if coin not in coins:
            coins[coin] = {
                "balance": 0.0,
                "usd": 0.0,
                "price": prices.get(coin, 0.0)
            }

    for coin, coin_info in coins.items():
        coin_price = coin_info["price"]
        st.markdown(f"### {coin} — ${coin_info['usd']:,.2f} ({coin_info['balance']:.4f})")

        with st.expander("Buy/Sell", expanded=False):
            col1, col2 = st.columns(2)

            max_buy_usd = float(max(usd_balance, 0.0))
            max_sell_usd = float(max(coin_info["usd"], 0.0))

            buy_key = f"buy_usd_input_{coin}_{mode}_{user_id}"
            sell_key = f"sell_usd_input_{coin}_{mode}_{user_id}"

            if buy_key not in st.session_state:
                st.session_state[buy_key] = 0.0
            if sell_key not in st.session_state:
                st.session_state[sell_key] = 0.0

            with col1:
                st.subheader("Buy")
                if st.button("Max (Buy)", key=f"buy_max_btn_{coin}"):
                    st.session_state[buy_key] = round(max_buy_usd, 2)

                st.number_input("Amount (USD)", 0.0, max_buy_usd, step=0.01, format="%.2f", key=buy_key)
                usd_amount = st.session_state[buy_key]
                coin_amt = usd_amount / coin_price if coin_price > 0 else 0.0
                st.write(f"Equivalent: **{coin_amt:.6f} {coin}**")

                if st.button(f"Buy {coin}", key=f"buy_btn_{coin}"):
                    if usd_amount > 0:
                        if mode == "paper":
                            simulate_trade(user_id, coin, "buy", coin_amt, coin_price)
                        else:
                            execute_trade(user_id, coin, "buy", coin_amt, coin_price)
                        st.success(f"✅ Bought {coin_amt:.6f} {coin}")
                        st.rerun()

            with col2:
                st.subheader("Sell")
                if st.button("Max (Sell)", key=f"sell_max_btn_{coin}"):
                    st.session_state[sell_key] = round(max_sell_usd, 2)

                st.number_input("Amount (USD)", 0.0, max_sell_usd, step=0.01, format="%.2f", key=sell_key)
                sell_usd = st.session_state[sell_key]
                sell_amt = sell_usd / coin_price if coin_price > 0 else 0.0
                st.write(f"Equivalent: **{sell_amt:.6f} {coin}**")

                if st.button(f"Sell {coin}", key=f"sell_btn_{coin}"):
                    if sell_amt > 0:
                        if mode == "paper":
                            simulate_trade(user_id, coin, "sell", sell_amt, coin_price)
                        else:
                            execute_trade(user_id, coin, "sell", sell_amt, coin_price)
                        st.success(f"✅ Sold {sell_amt:.6f} {coin}")
                        st.rerun()

    # Portfolio Pie Chart
    labels, values = ["USD"], [usd_balance]
    for coin, info in coins.items():
        if info["usd"] > 0:
            labels.append(coin)
            values.append(info["usd"])

    if len(labels) > 1:
        fig = px.pie(names=labels, values=values, title="Current Portfolio Breakdown", hole=0.4)
        fig.update_layout(height=400, width=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No valid data to display pie chart.")
