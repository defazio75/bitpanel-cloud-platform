import sys
import os
import json
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

from utils.config import get_mode
from utils.kraken_wrapper import get_prices

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bots")))
from rebalance_bot import rebalance_hodl

# === Determine Mode ===
def get_portfolio_file(mode, user_id):
    folder = "json_paper" if mode == "paper" else "json_live"
    return os.path.join("data", folder, user_id, "portfolio", "portfolio_snapshot.json")

def get_state_path(coin, mode, user_id):
    return os.path.join("data", f"json_{mode}", user_id, "current", f"{coin}_state.json")

def load_target_usd(coin, mode, user_id):
    path = get_state_path(coin, mode, user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            state = json.load(f)
        return state.get("HODL", {}).get("target_usd", 0.0)
    return 0.0

def save_target_usd(coin, mode, user_id, target_usd):
    path = get_state_path(coin, mode, user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            state = json.load(f)
    else:
        state = {}

    if "HODL" not in state:
        state["HODL"] = {}

    state["HODL"]["target_usd"] = round(target_usd, 2)

    with open(path, "w") as f:
        json.dump(state, f, indent=2)

    return True

def render(mode=None, user_id=None):
    st.write("Active Mode:", mode)
    st.title("🎯 Coin Allocation")

    if mode is None:
        mode = get_mode(user_id)

    folder = "json_paper" if mode == "paper" else "json_live"
    PORTFOLIO_FILE = get_portfolio_file(mode, user_id)

    st.caption(f"🛠 Mode: **{mode.upper()}**")

    portfolio_data = {
        "usd_balance": 0,
        "coins": {},
        "total_value": 0
    }

    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            snapshot = json.load(f)

        prices = get_prices()
        usd_balance = snapshot.get("usd_balance", 0)
        portfolio_data["usd_balance"] = usd_balance

        total_value = usd_balance

        for coin, info in snapshot.get("coins", {}).items():
            balance = info.get("balance", 0)
            price = prices.get(coin, 0)
            usd_value = round(balance * price, 2)

            portfolio_data["coins"][coin] = {
                "balance": balance,
                "price": price,
                "usd": usd_value
            }
            total_value += usd_value

        total_value = usd_balance
        for coin, info in snapshot.get("coins", {}).items():
            price = prices.get(coin, 0)
            balance = info.get("balance", 0)
            total_value += balance * price

        portfolio_data["total_value"] = round(total_value, 2)

    coin_data = {}
    for coin, info in portfolio_data["coins"].items():
        target_usd = load_target_usd(coin, mode, user_id)
        coin_data[coin] = {
            "amount": info.get("balance", 0),
            "usd": info.get("usd", 0),
            "usd_target": target_usd
        }

    col_a, col_b = st.columns(2)
    col_a.metric("💼 Total Portfolio Value", f"${portfolio_data['total_value']:,.2f}")
    col_b.metric("💰 Available USD", f"${portfolio_data['usd_balance']:,.2f}")

    selected_coin = st.selectbox("Choose Coin", list(coin_data.keys()), key=f"select_coin_{user_id}")
    updated_allocations = {}

    if not coin_data:
        st.warning("No coin data available.")
        return

    col_left, col_right = st.columns([2, 1])

    data = coin_data.get(selected_coin, {})

    with col_left:
        st.markdown(
            f"💲 **Current {selected_coin} Value:** ${data['usd']:,.2f} ({data['amount']:.2f} {selected_coin})"
        )

        with st.expander("Buy/Sell", expanded=False):
            col1, col2 = st.columns(2)

            coin_price = portfolio_data["coins"][selected_coin]["price"]
            coin_balance = portfolio_data["coins"][selected_coin]["balance"]
            max_buy_usd = float(max(portfolio_data["usd_balance"], 0.0))
            max_sell_usd = float(max(coin_balance * coin_price, 0.0)) if coin_price > 0 else 0.0

            # Keys for session state
            buy_key = f"buy_usd_input_{selected_coin}_{mode}_{user_id}"
            sell_key = f"sell_usd_input_{selected_coin}_{mode}_{user_id}"

            # Initialize session state
            if buy_key not in st.session_state:
                st.session_state[buy_key] = 0.0
            if sell_key not in st.session_state:
                st.session_state[sell_key] = 0.0

                if st.button("Max (Buy)", key=f"buy_max_{selected_coin}_btn"):
                    st.session_state[buy_key] = round(max_buy_usd, 2)

            # BUY SECTION
            with col1:
                st.subheader("Buy")

                if st.button("Max (Buy)", key=f"buy_max_btn_{selected_coin}_{mode}_{user_id}"):
                    st.session_state[buy_key] = min(round(max_buy_usd, 2), float(f"{max_buy_usd:.2f}"))

                st.number_input(
                    "Amount (USD)",
                    min_value=0.0,
                    max_value=max_buy_usd,
                    step=0.01,
                    format="%.2f",
                    key=buy_key
                )

                usd_amount = float(st.session_state[buy_key])
                coin_amount = usd_amount / coin_price if coin_price > 0 else 0
                st.write(f"Equivalent: **{coin_amount:.6f} {selected_coin}** at ${coin_price:,.2f}")

                if st.button(f"Buy {selected_coin}", key=f"buy_btn_{selected_coin}_{mode}_{user_id}"):
                    st.success(f"Buying {coin_amount:.6f} {selected_coin} for ${usd_amount:,.2f}")
                    current_usd = data.get("usd", 0)
                    new_target_usd = round(current_usd + usd_amount, 2)
                    success = save_target_usd(selected_coin, mode, user_id, new_target_usd)
                    if success:
                        st.success("✅ Allocation updated. Rebalancing...")
                        rebalance_hodl(user_id=user_id)
                        st.rerun()

            # SELL SECTION
            with col2:
                st.subheader("Sell")

                if sell_key not in st.session_state:
                    st.session_state[sell_key] = 0.0

                if st.button("Max (Sell)", key=f"sell_max_btn_{selected_coin}_{mode}_{user_id}"):
                    st.session_state[sell_key] = float(f"{min(max_sell_usd, max_sell_usd - 0.01):.2f}")

                st.number_input(
                    "Amount (USD)",
                    min_value=0.0,
                    max_value=max_sell_usd,
                    step=0.01,
                    format="%.2f",
                    key=sell_key
                )

                sell_usd_amount = float(st.session_state[sell_key])
                sell_coin_amount = sell_usd_amount / coin_price if coin_price > 0 else 0
                st.write(f"Equivalent: **{sell_coin_amount:.6f} {selected_coin}** at ${coin_price:,.2f}")

                if st.button(f"Sell {selected_coin}", key=f"sell_btn_{selected_coin}_{mode}_{user_id}"):
                    st.warning(f"Selling {sell_coin_amount:.6f} {selected_coin} for ${sell_usd_amount:,.2f}")
                    current_usd = data.get("usd", 0)
                    new_target_usd = round(max(current_usd - sell_usd_amount, 0), 2)
                    success = save_target_usd(selected_coin, mode, user_id, new_target_usd)
                    if success:
                        st.success("✅ Allocation updated. Rebalancing...")
                        rebalance_hodl(user_id=user_id)
                        st.rerun()

    with col_right:
        coin_labels = []
        coin_values = []

        usd_balance = portfolio_data.get("usd_balance", 0)
        if usd_balance > 0:
            coin_labels.append("USD")
            coin_values.append(usd_balance)

        for coin, info in portfolio_data.get("coins", {}).items():
            value = info.get("usd", 0)
            if value > 0:
                coin_labels.append(coin)
                coin_values.append(value)

        if coin_labels and coin_values and len(coin_labels) == len(coin_values):
            fig = px.pie(
                names=coin_labels,
                values=coin_values,
                title="Current Portfolio Breakdown",
                hole=0.4
            )
            fig.update_layout(height=400, width=400)
            st.plotly_chart(fig, use_container_width=True, key="current_allocation_pie")
        else:
            st.info("No valid portfolio data available to display chart.")

