import streamlit as st
import matplotlib.pyplot as plt
import json
import os

def load_portfolio_snapshot():
    mode = st.session_state.get("mode", "paper")
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


def load_strategy_state(coin, strategy_options):
    mode = st.session_state.get("mode", "paper")
    path = f"config/strategy_allocations_{mode}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
        return data.get(coin, {strategy: (100 if strategy == "HODL" else 0) for strategy in strategy_options})
    else:
        return {strategy: (100 if strategy == "HODL" else 0) for strategy in strategy_options}


def save_strategy_state(coin, allocations):
    mode = st.session_state.get("mode", "paper")
    path = f"config/strategy_allocations_{mode}.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    else:
        data = {}
    data[coin] = allocations
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        json.dump(allocations, f, indent=2)

def render():
    st.title("🧠 Strategy Controls")

    strategy_options = ["HODL", "RSI 5-Min", "RSI 1-Hour", "Bollinger Bot"]

    try:
        alloc_test = load_strategy_state("BTC", strategy_options)
    except Exception as e:
        st.warning("⚠️ Unable to load strategy allocations for BTC.")


    coin_list = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]

    holdings_data = load_portfolio_snapshot()

    if "strategy_allocations" not in st.session_state:
        st.session_state.strategy_allocations = {
            coin: load_strategy_state(coin, strategy_options)
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

        expander_key = f"{coin}_expanded"
        if expander_key not in st.session_state:
            st.session_state[expander_key] = False

        with st.expander(f"🪙 {coin} — ${current_usd:,.2f} ({coin_amt} {coin}) — Strategy: {strategy_summary}", expanded=st.session_state[expander_key]):
            st.session_state[expander_key] = True

            # Strategy Toggles
            toggle_cols = st.columns(len(strategy_options))
            for idx, strategy in enumerate(strategy_options):
                with toggle_cols[idx]:
                    toggle_key = f"{coin}_{strategy}_toggle"
                    active = allocations[strategy] > 0
                    new_state = st.checkbox(strategy, value=active, key=toggle_key)
                    if new_state and allocations[strategy] == 0:
                        allocations[strategy] = 1
                        st.session_state.pending_strategy_changes[coin] = True
                    elif not new_state and allocations[strategy] > 0:
                        allocations[strategy] = 0
                        st.session_state.pending_strategy_changes[coin] = True

                    if strategy != "HODL" and allocations[strategy] > 0:
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
                            save_strategy_state(coin, allocations)
                            st.success(f"{coin} strategy updated.")
                            st.session_state.pending_strategy_changes[coin] = False
                            st.rerun()
                with col2:
                    if st.button(f"❌ Cancel {coin} Changes"):
                        st.session_state.strategy_allocations[coin] = load_strategy_state(coin, strategy_options)
                        st.session_state.pending_strategy_changes[coin] = False
                        st.rerun()

    st.divider()
    st.success("✅ Strategy Controls loaded.")
