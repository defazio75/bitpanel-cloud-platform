
import streamlit as st
import matplotlib.pyplot as plt
import json
import os
import pandas as pd
from utils.kraken_wrapper import get_prices

# === Strategy File Utilities ===
def get_strategy_path(mode, user_id):
    return os.path.join("config", user_id, f"strategy_allocations_{mode}.json")

def get_snapshot_path(mode, user_id):
    folder = "json_paper" if mode == "paper" else "json_live"
    return os.path.join("data", folder, user_id, "portfolio", "portfolio_snapshot.json")

def get_state_path(coin, mode, user_id):
    folder = f"json_{mode}"
    return os.path.join("data", folder, user_id, "current", f"{coin}_state.json")

def load_strategy_state(coin, strategy_options, mode, user_id):
    path = get_state_path(coin, mode, user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            state = json.load(f)
    else:
        state = {}

    return {strategy: state.get(strategy, {}).get("allocation", 0) for strategy in strategy_options}

def save_strategy_state(coin, allocations, mode, user_id):
    path = get_state_path(coin, mode, user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            state = json.load(f)
    else:
        state = {}

    for strategy, allocation in allocations.items():
        if strategy not in state:
            state[strategy] = {}
        state[strategy]["allocation"] = allocation

    with open(path, "w") as f:
        json.dump(state, f, indent=2)

def save_full_strategy_breakdown(coin, allocations, coin_amt, coin_usd, mode, user_id):
    path = get_strategy_path(mode, user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    else:
        data = {}

    data[coin] = allocations

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_portfolio_snapshot(mode, user_id):
    path = get_snapshot_path(mode, user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def render(mode, user_id):
    st.title("🧠 Strategy Controls")

    strategy_options = ["HODL", "RSI 5-Min", "RSI 1-Hour", "Bollinger Bot", "DCA Matrix"]

    prices = get_prices()

    try:
        alloc_test = load_strategy_state("BTC", strategy_options, mode, user_id)
    except Exception as e:
        st.warning("⚠️ Unable to load strategy allocations for BTC.")

    coin_list = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]

    holdings_data = load_portfolio_snapshot(mode, user_id)

    if "strategy_allocations" not in st.session_state:
        st.session_state.strategy_allocations = {
            coin: load_strategy_state(coin, strategy_options, mode)
            for coin in coin_list
        }

    if "pending_strategy_changes" not in st.session_state:
        st.session_state.pending_strategy_changes = {
            coin: False for coin in coin_list
        }

    if "sell_only_profit_flags" not in st.session_state:
        st.session_state.sell_only_profit_flags = {
            coin: {strategy: False for strategy in strategy_options if strategy != "HODL"}
            for coin in coin_list
        }

    for coin in coin_list:
        allocations = st.session_state.strategy_allocations[coin]
        pending_change = st.session_state.pending_strategy_changes[coin]

        active_strategies = [s for s, pct in allocations.items() if pct > 0]
        strategy_summary = f"{active_strategies[0]}" if len(active_strategies) == 1 else f"Multiple ({len(active_strategies)})"
        coin_data = holdings_data.get(coin, {"usd": 0, "amt": 0})
        current_usd = coin_data["usd"]
        coin_amt = coin_data["amt"]

        if current_usd <= 0 and coin_amt <= 0:
            continue

        expander_key = f"{coin}_expanded"
        if expander_key not in st.session_state:
            st.session_state[expander_key] = False

        with st.expander(f"🪙 {coin} — ${current_usd:,.2f} ({coin_amt} {coin}) — Strategy: {strategy_summary}", expanded=st.session_state[expander_key]):
            st.session_state[expander_key] = True

            strategy_live_values = {}
            coin_price = prices.get(coin, 0)
            state_path = f"data/json_{mode}/{user_id}/current/{coin}_state.json"
            if os.path.exists(state_path):
                with open(state_path, "r") as f:
                    strategy_states = json.load(f)
                for strat in strategy_options:
                    strat_info = strategy_states.get(strat, {})
                    amount = strat_info.get("amount", 0)
                    strategy_live_values[strat] = round(amount * coin_price, 2)
            else:
                for strat in strategy_options:
                    strategy_live_values[strat] = 0.0

            # Strategy Table
            strat_data = []
            for strat, alloc in allocations.items():
                active = alloc > 0
                live_value = strategy_live_values.get(strat, 0)

                if alloc == 0:
                    status = "Inactive"
                elif live_value > 0:
                    status = "Holding"
                else:
                    status = "Waiting"

                strat_data.append({
                    "Strategy": strat,
                    "Value (Live USD)": f"${live_value:,.2f}",
                    "Active": "✅" if active else "❌",
                    "Status": status
                })
            df = pd.DataFrame(strat_data)
            df.set_index("Strategy", inplace=True)
            st.table(df)

            # Strategy Toggles
            toggle_cols = st.columns(len(strategy_options))
            for idx, strategy in enumerate(strategy_options):
                with toggle_cols[idx]:
                    toggle_key = f"{coin}_{strategy}_toggle"
                    active = allocations.get(strategy, 0) > 0
                    new_state = st.checkbox(strategy, value=active, key=toggle_key)
                    if new_state and allocations.get(strategy, 0) == 0:
                        allocations[strategy] = 1
                        st.session_state.pending_strategy_changes[coin] = True
                    elif not new_state and allocations.get(strategy, 0) > 0:
                        allocations[strategy] = 0
                        st.session_state.pending_strategy_changes[coin] = True

                    if strategy != "HODL" and allocations.get(strategy, 0) > 0:
                        profit_flag_key = f"{coin}_{strategy}_profit_only"
                        current_flag = st.session_state.sell_only_profit_flags[coin][strategy]
                        new_flag = st.checkbox("Sell only in profit?", value=current_flag, key=profit_flag_key)
                        st.session_state.sell_only_profit_flags[coin][strategy] = new_flag

            st.markdown("---")
            active_allocs = {s: a for s, a in allocations.items() if a > 0}
            total_alloc = sum(active_allocs.values())

            slider_cols = st.columns(len(active_allocs) + 1)
            for idx, (strategy, value) in enumerate(active_allocs.items()):
                with slider_cols[idx]:
                    st.markdown(f"**{strategy}**")
                    max_allowed = 100 - (total_alloc - value)
                    alloc_pct = st.slider(
                        label="",
                        min_value=0,
                        max_value=int(max_allowed),
                        value=value,
                        key=f"{coin}_{strategy}_slider",
                        label_visibility="collapsed"
                    )
                    if alloc_pct != allocations[strategy]:
                        allocations[strategy] = alloc_pct
                        st.session_state.pending_strategy_changes[coin] = True
                    st.markdown(f"`{alloc_pct}%`")
                    alloc_usd = round((alloc_pct / 100) * current_usd, 2)
                    st.markdown(f"Allocated: `${alloc_usd:,.2f}`")

            with slider_cols[-1]:
                if active_allocs:
                    labels = list(active_allocs.keys())
                    sizes = list(active_allocs.values())
                    fig, ax = plt.subplots()
                    ax.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
                    ax.axis('equal')
                    st.pyplot(fig)

            if st.session_state.pending_strategy_changes[coin]:
                st.warning("Changes detected. Save your strategy allocation?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Confirm {coin} Strategy Allocation"):
                        total_check = sum(allocations.values())
                        if total_check != 100:
                            st.error("Allocations must equal 100%")
                        else:
                            save_strategy_state(coin, allocations, mode, user_id)
                            save_full_strategy_breakdown(coin, allocations, coin_amt, current_usd, mode, user_id)
                            st.success(f"{coin} strategy updated.")
                            st.session_state.pending_strategy_changes[coin] = False
                            st.rerun()
                with col2:
                    if st.button(f"❌ Cancel {coin} Changes"):
                        st.session_state.strategy_allocations[coin] = load_strategy_state(coin, strategy_options, mode, user_id)
                        st.session_state.pending_strategy_changes[coin] = False
                        st.rerun()

    st.divider()
    st.success("✅ Strategy Controls loaded.")
