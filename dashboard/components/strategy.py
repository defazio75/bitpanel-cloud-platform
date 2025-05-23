
import streamlit as st
import matplotlib.pyplot as plt
import json
import os
import pandas as pd
from utils.kraken_wrapper import get_prices

def load_portfolio_snapshot(mode):
    file_path = f"data/json_{mode}/portfolio/portfolio_snapshot.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            raw = json.load(f)
        coins = raw.get("coins", {})
        return {
            coin: {
                "amt": data["balance"],
                "usd": round(data["balance"] * data["price"], 2)
            }
            for coin, data in coins.items()
        }
    else:
        st.error("❌ Portfolio file not found.")
    return {}

def load_strategy_state(coin, strategy_options, mode):
    path = f"config/strategy_allocations_{mode}.json"

    # Mapping from internal bot keys to UI display names
    internal_to_display_map = {
        "RSI_5MIN": "RSI 5-Min",
        "RSI_1HR": "RSI 1-Hour",
        "BOLLINGER": "Bollinger Bot",
        "DCA_MATRIX": "DCA Matrix",
        "HODL": "HODL"
    }

    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)

        raw = data.get(coin, {})
        return {
            internal_to_display_map.get(k, k): v for k, v in raw.items()
            if internal_to_display_map.get(k, k) in strategy_options
        }

    return {strategy: (100 if strategy == "HODL" else 0) for strategy in strategy_options}

def save_strategy_state(coin, allocations, mode):
    path = f"config/strategy_allocations_{mode}.json"

    # Load existing or create new
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    else:
        data = {}

    # ✅ Remap UI keys to internal bot keys
    strategy_key_map = {
        "RSI 5-Min": "RSI_5MIN",
        "RSI 1-Hour": "RSI_1HR",
        "Bollinger Bot": "BOLLINGER",
        "DCA Matrix": "DCA_MATRIX",
        "HODL": "HODL"
    }

    data[coin] = {
        strategy_key_map.get(k, k): v for k, v in allocations.items()
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def save_full_strategy_breakdown(coin, allocations, coin_amt, coin_usd, mode):
    state_path = f"data/json_{mode}/current/{coin}_state.json"
    prices = get_prices()
    price = prices.get(coin, 0)

    strategy_key_map = {
        "RSI 5-Min": "RSI_5MIN",
        "RSI 1-Hour": "RSI_1HR",
        "Bollinger Bot": "BOLLINGER",
        "DCA Matrix": "DCA_MATRIX",
        "HODL": "HODL"
    }

    state = {}
    for strategy_display, percent in allocations.items():
        strategy_key = strategy_key_map.get(strategy_display, strategy_display)
        allocation_usd = (percent / 100) * coin_usd
        allocation_amt = allocation_usd / price if price > 0 else 0
        state[strategy_key] = {
            "amount": round(allocation_amt, 8),
            "usd_held": 0.0,
            "status": "Holding" if percent > 0 else "Inactive",
            "buy_price": price
        }

    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

def render(mode):
    st.title("🧠 Strategy Controls")

    strategy_options = ["HODL", "RSI 5-Min", "RSI 1-Hour", "Bollinger Bot", "DCA Matrix"]

    prices = get_prices()

    try:
        alloc_test = load_strategy_state("BTC", strategy_options, mode)
    except Exception as e:
        st.warning("⚠️ Unable to load strategy allocations for BTC.")

    coin_list = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]

    holdings_data = load_portfolio_snapshot(mode)

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
            state_path = f"data/json_{mode}/current/{coin}_state.json"
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
                            save_strategy_state(coin, allocations, mode)
                            save_full_strategy_breakdown(coin, allocations, coin_amt, current_usd, mode)
                            st.success(f"{coin} strategy updated.")
                            st.session_state.pending_strategy_changes[coin] = False
                            st.rerun()
                with col2:
                    if st.button(f"❌ Cancel {coin} Changes"):
                        st.session_state.strategy_allocations[coin] = load_strategy_state(coin, strategy_options, mode)
                        st.session_state.pending_strategy_changes[coin] = False
                        st.rerun()

    st.divider()
    st.success("✅ Strategy Controls loaded.")
