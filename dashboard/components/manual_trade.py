import streamlit as st
import sys
import os
from datetime import datetime
from utils.config import get_mode
from utils.kraken_wrapper import get_prices
from utils.firebase_db import load_portfolio_snapshot
from utils.trade_simulator import simulate_trade
from utils.trade_executor import execute_trade

def render_manual_trade(user_id, token, mode):
    if not token and "token" in st.session_state:
        token = st.session_state.token

    st.title("🛒 Manual Trade")

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

    SUPPORTED_COINS = ["No Coin Selected", "BTC", "ETH", "SOL", "XRP", "LINK", "DOT"]

    with st.expander("Trade", expanded=True):
        selected_coin = st.selectbox("Select a Coin", SUPPORTED_COINS, key="manual_selected_coin")

        if selected_coin == "No Coin Selected":
            st.info("Please select a coin to continue.")
            return

        st.markdown(f"### What would you like to do with {selected_coin}?")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"💸 Buy {selected_coin}"):
                st.session_state["trade_action"] = "buy"
                st.session_state["trade_coin"] = selected_coin
                st.switch_page("dashboard/components/manual_trade_checkout.py")

        with col2:
            if st.button(f"💰 Sell {selected_coin}"):
                st.session_state["trade_action"] = "sell"
                st.session_state["trade_coin"] = selected_coin
                st.switch_page("dashboard/components/manual_trade_checkout.py")
