import streamlit as st
import sys
import os
from datetime import datetime

from utils.kraken_wrapper import get_prices
from utils.firebase_db import load_portfolio_snapshot
from utils.trade_simulator import simulate_trade
from utils.trade_executor import execute_trade

def render_manual_trade(mode, user_id, token):
    st.title("💸 Manual Trade")
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

    st.markdown(f"**💵 Available USD:** `${usd_balance:,.2f}`")
    st.markdown("### 🛒 Trade Now")

    selected_coin = st.selectbox("Select a Coin", SUPPORTED_COINS)
    coin_price = coins[selected_coin]["price"]
    coin_balance = coins[selected_coin]["balance"]
    coin_usd_value = coins[selected_coin]["usd"]

    buy_key = f"buy_amount_input_{selected_coin}"
    sell_key = f"sell_amount_input_{selected_coin}"
    buy_trigger_key = f"max_buy_triggered_{selected_coin}"
    sell_trigger_key = f"max_sell_triggered_{selected_coin}"

    col1, col2 = st.columns(2)

    # BUY section
    with col1:
        st.subheader("Buy")
        max_buy = usd_balance

        buy_col1, buy_col2 = st.columns([3, 1])
        
        with buy_col1:
            default_buy_value = max_buy if st.session_state.get(buy_trigger_key, False) else 0.0
            buy_amount = st.number_input(
                "Amount to Buy (USD)",
                min_value=0.0,
                max_value=max_buy,
                value=default_buy_value,
                step=1.0,
                format="%.2f",
                key=buy_key
            )

        with buy_col2:
            if st.button("Max Buy"):
                st.session_state[buy_trigger_key] = True
                st.rerun()

        buy_qty = round(buy_amount / coin_price, 6) if coin_price > 0 and buy_amount > 0 else 0.0
        st.write(f"Estimated: **{buy_qty} {selected_coin}**")

        if st.button(f"Execute Buy {selected_coin}"):
            if buy_amount <= 0:
                st.error("❌ Please enter USD amount greater than 0.")
            elif coin_price <= 0:
                st.error(f"❌ Invalid price for {selected_coin}. Please refresh or try again later.")
            else:
                try:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="ManualTrade",
                            action="buy",
                            amount=buy_qty,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id,
                            token=token
                        )
                    else:
                        execute_trade(
                            bot_name="ManualTrade",
                            action="buy",
                            amount=buy_qty,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id
                        )
                    st.success(f"✅ Bought {buy_qty:.6f} {selected_coin} at ${coin_price:.2f}")
                    st.session_state[buy_trigger_key] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Trade failed: {e}")

    # SELL section
    with col2:
        st.subheader("Sell")
        max_sell = coin_usd_value

        sell_col1, sell_col2 = st.columns([3, 1])
        with sell_col1:
            default_sell_value = max_sell if st.session_state.get(sell_trigger_key, False) else 0.0
            sell_amount = st.number_input(
                "Amount to Sell (USD)",
                min_value=0.0,
                max_value=max_sell,
                value=default_sell_value,
                step=1.0,
                format="%.2f",
                key=sell_key
            )

        with sell_col2:
            if st.button("Max Sell"):
                st.session_state[sell_trigger_key] = True
                st.rerun()

        sell_qty = round(sell_amount / coin_price, 6) if coin_price > 0 and sell_amount > 0 else 0.0
        st.write(f"Estimated: **{sell_qty} {selected_coin}**")

        if st.button(f"Execute Sell {selected_coin}"):
            if sell_amount <= 0:
                st.error("❌ Please enter a valid USD amount greater than 0.")
            elif coin_price <= 0:
                st.error(f"❌ Invalid price for {selected_coin}. Please refresh or try again later.")
            else:
                try:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="ManualTrade",
                            action="sell",
                            amount=sell_qty,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id,
                            token=token
                        )
                    else:
                        execute_trade(
                            bot_name="ManualTrade",
                            action="sell",
                            amount=sell_qty,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id
                        )
                    st.success(f"✅ Sold {sell_qty:.6f} {selected_coin} at ${coin_price:.2f}")
                    st.session_state[sell_trigger_key] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Trade failed: {e}")
