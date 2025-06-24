import streamlit as st
import sys
import os
from datetime import datetime

from utils.kraken_wrapper import get_prices
from utils.firebase_db import load_portfolio_snapshot
from utils.trade_simulator import simulate_trade
from utils.trade_executor import execute_trade

def render_manual_trade(mode, user_id, token):
    st.title("\U0001F4B8 Manual Trade")
    st.caption("Manually buy or sell crypto using your available balance.")

    # Load balances and prices
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    prices = get_prices(user_id=user_id)

    usd_balance = snapshot.get("usd_balance", 0.0)
    coin_data = snapshot.get("coins", {})

    SUPPORTED_COINS = ["BTC", "ETH", "SOL", "XRP", "LINK", "DOT"]
    coins = {}

    for coin in SUPPORTED_COINS:
        balance = coin_data.get(coin, {}).get("balance", 0.0)
        price = prices.get(coin, 0.0)
        usd_value = round(balance * price, 2)
        coins[coin] = {
            "balance": balance,
            "price": price,
            "usd": usd_value
        }

    st.markdown(f"**\U0001F4B5 Available USD:** `${usd_balance:,.2f}`")
    st.markdown("### \U0001F34E Trade Now")

    col1, col2 = st.columns(2)

    # BUY SECTION
    with col1:
        st.subheader("Buy")
        buy_amount_col, buy_button_col = st.columns([3, 1])

        with buy_amount_col:
            buy_amount = st.number_input("Buy Amount (USD)", min_value=0.0, step=1.0, format="%.2f", key="buy_amount")

        with buy_button_col:
            if st.button("Max Buy"):
                st.session_state.buy_amount = usd_balance
                st.rerun()

        buy_coin = st.selectbox("Coin to Buy", SUPPORTED_COINS, key="buy_coin")
        buy_price = prices.get(buy_coin, 0.0)
        buy_qty = round(st.session_state.get("buy_amount", 0.0) / buy_price, 6) if buy_price > 0 else 0.0
        st.write(f"Estimated: **{buy_qty} {buy_coin}**")

        if st.button(f"Execute Buy {buy_coin}", key="buy_exec"):
            if st.session_state.buy_amount <= 0:
                st.error("\u274c Please enter USD amount greater than 0.")
            elif buy_price <= 0:
                st.error(f"\u274c Invalid price for {buy_coin}. Please refresh or try again later.")
            else:
                try:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="ManualTrade",
                            action="buy",
                            amount=buy_qty,
                            price=buy_price,
                            mode=mode,
                            coin=buy_coin,
                            user_id=user_id,
                            token=token
                        )
                    else:
                        execute_trade(
                            bot_name="ManualTrade",
                            action="buy",
                            amount=buy_qty,
                            price=buy_price,
                            mode=mode,
                            coin=buy_coin,
                            user_id=user_id
                        )
                    st.success(f"\u2705 Bought {buy_qty:.6f} {buy_coin} at ${buy_price:.2f}")
                except Exception as e:
                    st.error(f"\u274c Trade failed: {e}")

    # SELL SECTION
    with col2:
        st.subheader("Sell")
        sell_amount_col, sell_button_col = st.columns([3, 1])

        with sell_amount_col:
            sell_amount = st.number_input("Sell Amount (USD)", min_value=0.0, step=1.0, format="%.2f", key="sell_amount")

        with sell_button_col:
            sell_coin = st.session_state.get("sell_coin", "BTC")
            coin_usd_val = coins.get(sell_coin, {}).get("usd", 0.0)
            if st.button("Max Sell"):
                st.session_state.sell_amount = coin_usd_val
                st.rerun()

        sell_coin = st.selectbox("Coin to Sell", SUPPORTED_COINS, key="sell_coin")
        sell_price = prices.get(sell_coin, 0.0)
        sell_qty = round(st.session_state.get("sell_amount", 0.0) / sell_price, 6) if sell_price > 0 else 0.0
        st.write(f"Estimated: **{sell_qty} {sell_coin}**")

        if st.button(f"Execute Sell {sell_coin}", key="sell_exec"):
            if st.session_state.sell_amount <= 0:
                st.error("\u274c Please enter USD amount greater than 0.")
            elif sell_price <= 0:
                st.error(f"\u274c Invalid price for {sell_coin}. Please refresh or try again later.")
            else:
                try:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="ManualTrade",
                            action="sell",
                            amount=sell_qty,
                            price=sell_price,
                            mode=mode,
                            coin=sell_coin,
                            user_id=user_id,
                            token=token
                        )
                    else:
                        execute_trade(
                            bot_name="ManualTrade",
                            action="sell",
                            amount=sell_qty,
                            price=sell_price,
                            mode=mode,
                            coin=sell_coin,
                            user_id=user_id
                        )
                    st.success(f"\u2705 Sold {sell_qty:.6f} {sell_coin} at ${sell_price:.2f}")
                except Exception as e:
                    st.error(f"\u274c Trade failed: {e}")
