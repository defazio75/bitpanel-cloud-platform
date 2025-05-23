from streamlit_autorefresh import st_autorefresh
import streamlit as st
import json
import os
import pandas as pd
import time
from utils.kraken_wrapper import get_prices_with_change, get_rsi, get_bollinger_bandwidth, get_live_balances

from config.config import get_mode

@st.cache_data(ttl=10)
def get_live_price_data():
    return get_prices_with_change()

def load_strategy_state(coin, mode):
    path = f"data/json_{mode}/current/{coin}_state.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def load_strategy_allocations(mode):
    filename = f"strategy_allocations_{mode}.json"
    path = os.path.join("config", filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def load_live_balances(mode):
    if mode == "live":
        return get_live_balances()
    else:
        path = f"data/json_paper/portfolio/portfolio_snapshot.json"
        if os.path.exists(path):
            with open(path, "r") as f:
                snapshot = json.load(f)
                return {coin: data["balance"] for coin, data in snapshot.get("coins", {}).items()}
        return {}

def render(mode):
    st_autorefresh(interval=10 * 1000, key="price_autorefresh")
    st.title("📍 Current Positions")

    mode = get_mode()
    strategy_allocs = load_strategy_allocations(mode)

    # === Mode-specific balances and prices
    if mode == "paper":
        snapshot_path = "data/json_paper/portfolio/portfolio_snapshot.json"
        with open(snapshot_path, "r") as f:
            snapshot = json.load(f)

        balances = {
            coin.upper(): data.get("balance", 0.0)
            for coin, data in snapshot.get("coins", {}).items()
        }

        prices_data = get_prices_with_change()

    else:
        balances = get_live_balances()
        prices_data = get_prices_with_change()

    for coin, strategies in strategy_allocs.items():
        coin_balance = balances.get(coin, 0)
        #if coin_balance == 0:
            #continue

        coin_state = load_strategy_state(coin, mode)
        price_info = prices_data.get(coin, {})
        price = price_info.get("price", 0)
        change = price_info.get("change", 0)
        pct = price_info.get("pct_change", 0)
        total_value = coin_balance * price 

        if total_value <= 0:
            continue

        # Expander label is now the holdings line
        expander_label = f"💰 Total {coin} Holdings: ${total_value:,.2f}"
        expander_key = f"{coin}_expander_open"
        if expander_key not in st.session_state:
            st.session_state[expander_key] = False
        with st.expander(expander_label, expanded=st.session_state[expander_key]):
            st.session_state[expander_key] = True

            # Clean Price Display
            direction = "▲" if change > 0 else "▼"
            change_color = "#4CAF50" if change > 0 else "#F44336"

            st.markdown(f"""
                <div style="font-size:18px; margin-bottom: 10px;">
                    💲 <b>{coin} Price:</b> ${price:,.2f} 
                    <span style="color:{change_color}; font-weight:normal;">
                        {direction} {abs(change):.2f} ({abs(pct):.2f}%)
                    </span>
                </div>
            """, unsafe_allow_html=True)

            # === Strategy Table
            trade_rows = []
            for strat, alloc in strategies.items():
                if "5-min" in strat.lower():
                    interval = "5m"
                elif "1-hour" in strat.lower():
                    interval = "1h"
                else:
                    interval = "1h"
                state = coin_state.get(strat, {})
                status = state.get("status", "Inactive")
                amount = float(state.get("amount", 0.0))
                buy_price = float(state.get("buy_price", 0.0))
                usd_held = float(state.get("usd_held", 0.0))
                current_price = float(price)
                current_value = (amount * current_price) + usd_held
                pl = (current_price - buy_price) * amount if buy_price else 0.0
                pct_gain = ((current_price - buy_price) / buy_price * 100) if buy_price else 0.0
                rsi_val = get_rsi(coin, interval)
                bb_val = get_bollinger_bandwidth(coin, interval)

                # Show indicator based on strategy type
                indicator = "–"
                if "rsi" in strat.lower():
                    indicator = f"RSI {rsi_val:.2f}" if rsi_val is not None else "RSI –"
                elif "bollinger" in strat.lower():
                    indicator = f"BB {bb_val:.4f}" if bb_val is not None else "BB –"

                # Improve Status display if allocated but inactive
                if alloc > 0 and status == "Inactive":
                    status = "Waiting"

                trade_rows.append({
                    "Strategy": strat,
                    "Strategy Holdings": f"${current_value:,.2f}",
                    "Active": "✅" if alloc > 0 else "❌",
                    "Indicator": indicator,
                    "Status": status,
                    "Bought Price": f"${buy_price:,.2f}" if buy_price else "–",
                    "P/L ($)": f"<span style='color:{'#4CAF50' if pl > 0 else '#F44336' if pl < 0 else '#999'};'>${pl:,.2f}</span>",
                    "% Gain/Loss": (
                        f"<span style='color:{'#4CAF50' if pct_gain > 0 else '#F44336' if pct_gain < 0 else '#999'};'>"
                        f"{pct_gain:.2f}%</span>" if buy_price else "–"
                    )
                })

            df = pd.DataFrame(trade_rows)
            df.index = [''] * len(df)
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)