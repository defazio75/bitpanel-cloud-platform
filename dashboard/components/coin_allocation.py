import sys
import os
import streamlit as st
import time
import matplotlib.pyplot as plt
import plotly.express as px
from utils.kraken_wrapper import get_prices, get_live_balances
from utils.config import get_mode
from utils.firebase_db import load_portfolio_snapshot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bots")))
from utils.trade_simulator import simulate_trade
from utils.trade_executor import execute_trade

@st.cache_data(ttl=300)  # Cache live prices and portfolio for 5 minutes
def get_cached_snapshot(user_id, token, mode):
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    prices = get_prices(user_id=user_id)
    return snapshot, prices

def render_coin_allocation(mode, user_id, token):
    if not token and "token" in st.session_state:
        token = st.session_state.token

    st.title("🎯 Coin Allocation")
    if mode is None:
        mode = get_mode(user_id)

    st.caption(f"🛠 Mode: **{mode.upper()}**")

    snapshot, prices = get_cached_snapshot(user_id, token, mode)

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

    SUPPORTED_COINS = ["BTC", "ETH", "SOL", "XRP", "LINK", "DOT"]
    for coin in SUPPORTED_COINS:
        if coin not in coins:
            coins[coin] = {
                "balance": 0.0,
                "usd": 0.0,
                "price": prices.get(coin, 0.0)
            }

    with st.expander("Trade", expanded=False):
        selected_coin = st.selectbox("Select a Coin", list(coins.keys()), key=f"select_coin_{user_id}")
        coin_info = coins[selected_coin]
        coin_price = coin_info["price"]

        col1, col2 = st.columns(2)
        max_buy_usd = float(max(usd_balance, 0.0))
        max_sell_usd = float(max(coin_info["usd"], 0.0))

        buy_key = f"buy_usd_input_{selected_coin}_{mode}_{user_id}"
        sell_key = f"sell_usd_input_{selected_coin}_{mode}_{user_id}"

        with col1:
            st.subheader("Buy")

            # Trigger Max Buy
            if st.button("Max (Buy)", key=f"buy_max_btn_{selected_coin}"):
                st.session_state[buy_key] = round(max_buy_usd, 2)
                st.rerun()

            # Let Streamlit manage the input naturally
            buy_usd_input = st.number_input(
                "Amount (USD)",
                min_value=0.0,
                max_value=max_buy_usd,
                step=0.01,
                format="%.2f",
                key=buy_key
            )

            coin_amt = buy_usd_input / coin_price if coin_price > 0 else 0.0
            st.write(f"Equivalent: **{coin_amt:.6f} {selected_coin}**")

            if st.button(f"Buy {selected_coin}", key=f"buy_btn_{selected_coin}"):
                if buy_usd_input > 0:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="ManualTrade",
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
                            bot_name="ManualTrade",
                            action="buy",
                            amount=coin_amt,
                            price=coin_price,
                            coin=selected_coin,
                            user_id=user_id,
                            mode=mode
                        )
                    st.success(f"✅ Bought {coin_amt:.6f} {selected_coin}")
                    st.rerun()

        with col2:
            st.subheader("Sell")

            if st.button("Max (Sell)", key=f"sell_max_btn_{selected_coin}"):
                st.session_state[sell_key] = round(max_sell_usd, 2)
                st.rerun()

            sell_usd_input = st.number_input(
                "Amount (USD)",
                min_value=0.0,
                max_value=max_sell_usd,
                step=0.01,
                format="%.2f",
                key=sell_key
            )

            sell_amt = sell_usd_input / coin_price if coin_price > 0 else 0.0
            st.write(f"Equivalent: **{sell_amt:.6f} {selected_coin}**")

            if st.button(f"Sell {selected_coin}", key=f"sell_btn_{selected_coin}"):
                if sell_amt > 0:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="ManualTrade",
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
                            bot_name="ManualTrade",
                            action="sell",
                            amount=sell_amt,
                            price=coin_price,
                            coin=selected_coin,
                            user_id=user_id,
                            mode=mode
                        )
                    st.success(f"✅ Sold {sell_amt:.6f} {selected_coin}")
                    st.rerun()
