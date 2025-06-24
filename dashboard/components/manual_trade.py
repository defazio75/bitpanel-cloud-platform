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

    with st.expander("Trade", expanded=True):
        selected_coin = st.selectbox("Select a Coin", list(coins.keys()), key=f"select_coin_{user_id}")
        coin_info = coins[selected_coin]
        coin_price = coin_info["price"]

        col1, col2 = st.columns(2)
        max_buy_usd = float(max(usd_balance, 0.0))
        max_sell_usd = float(max(coin_info["usd"], 0.0))

        buy_key = f"buy_usd_input_{selected_coin}_{mode}_{user_id}"
        sell_key = f"sell_usd_input_{selected_coin}_{mode}_{user_id}"

        if buy_key not in st.session_state:
            st.session_state[buy_key] = 0.0
        if sell_key not in st.session_state:
            st.session_state[sell_key] = 0.0

        with col1:
            st.subheader("Buy")
            if st.button("Max (Buy)", key=f"max_buy_btn_{selected_coin}"):
                st.session_state[buy_key] = round(max_buy_usd, 2)
                st.rerun

            buy_input = st.number_input(
                "Amount to Buy (USD)",
                min_value=0.0,
                max_value=max_buy_usd,
                value=st.session_state[buy_key],
                step=0.01,
                format="%.2f",
                key=buy_key
            )

            coin_amt = buy_input / coin_price if coin_price > 0 else 0.0
            st.write(f"Equivalent: **{coin_amt:.6f} {selected_coin}**")

            if st.button(f"Buy {selected_coin}", key=f"buy_confirm_btn_{selected_coin}"):
                if buy_input > 0:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="HODL",
                            action="buy",
                            amount=coin_amt,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id,
                            token=token
                        )
                    else:
                        execute_trade(
                            bot_name="HODL",
                            action="buy",
                            amount=coin_amt,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id,
                            token=token
                        )
                    st.success(f"✅ Bought {coin_amt:.6f} {selected_coin}")
                    st.rerun

        with col2:
            st.subheader("Sell")
            if st.button("Max (Sell)", key=f"max_sell_btn_{selected_coin}"):
                st.session_state[sell_key] = round(max_sell_usd, 2)
                st.experimental_rerun()

            sell_input = st.number_input(
                "Amount to Sell (USD)",
                min_value=0.0,
                max_value=max_sell_usd,
                value=st.session_state[sell_key],
                step=0.01,
                format="%.2f",
                key=sell_key
            )

            sell_amt = sell_input / coin_price if coin_price > 0 else 0.0
            st.write(f"Equivalent: **{sell_amt:.6f} {selected_coin}**")

            if st.button(f"Sell {selected_coin}", key=f"sell_confirm_btn_{selected_coin}"):
                if sell_input > 0:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="HODL",
                            action="sell",
                            amount=sell_amt,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id,
                            token=token
                        )
                    else:
                        execute_trade(
                            bot_name="HODL",
                            action="sell",
                            amount=sell_amt,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id,
                            token=token
                        )
                    st.success(f"✅ Sold {sell_amt:.6f} {selected_coin}")
                    st.rerun
