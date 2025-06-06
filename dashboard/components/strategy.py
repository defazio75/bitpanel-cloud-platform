import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from utils.kraken_wrapper import get_prices
from utils.config import get_mode
from utils.firebase_db import (
    load_user_profile,
    load_strategy_allocations,
    load_portfolio_snapshot,
    load_coin_state,
    load_performance_snapshot
)

def load_strategy_state(coin, strategy_options, user_id, token, mode):
    data = load_coin_state(user_id, coin, token, mode)
    return data if data else {}

def save_strategy_state(coin, allocations, user_id, token, mode):
    current_data = load_coin_state(user_id, coin, token, mode) or {}
    for strategy, allocation in allocations.items():
        if strategy not in current_data:
            current_data[strategy] = {}
        current_data[strategy]["allocation"] = allocation
    save_coin_state(user_id, coin, current_data, token, mode)

def save_full_strategy_breakdown(coin, allocations, coin_amt, coin_usd, user_id, token, mode):
    # Save full strategy allocations to Firebase using existing save_strategy_allocations logic
    current_allocations = {
        "coin": coin,
        "allocations": allocations,
        "coin_amt": coin_amt,
        "coin_usd": coin_usd
    }
    save_strategy_allocations(user_id, current_allocations, token, mode)

def render(mode, user_id, token):
    st.title("🧠 Strategy Controls")

    strategy_options = ["HODL", "RSI 5-Min", "RSI 1-Hour", "Bollinger Bot", "DCA Matrix"]
    coin_list = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]
    prices = get_prices(user_id=user_id)

    if "user" not in st.session_state:
        st.warning("⚠️ Please log in to access strategy controls.")
        return

    token = st.session_state.user.get("token", "")
    holdings_data = load_portfolio_snapshot(user_id=user_id, token=token, mode=mode)

    if "strategy_allocations" not in st.session_state:
        st.session_state.strategy_allocations = {
            coin: load_strategy_state(coin, strategy_options, user_id, token, mode)
            for coin in coin_list
        }

    if "pending_strategy_changes" not in st.session_state:
        st.session_state.pending_strategy_changes = {coin: False for coin in coin_list}

    if "sell_only_profit_flags" not in st.session_state:
        st.session_state.sell_only_profit_flags = {
            coin: {strategy: False for strategy in strategy_options if strategy != "HODL"}
            for coin in coin_list
        }

    for coin in coin_list:
        allocations = st.session_state.strategy_allocations[coin]
        pending_change = st.session_state.pending_strategy_changes[coin]
        active_strategies = [s for s, v in allocations.items() if isinstance(v, dict) and v.get("allocation", 0) > 0]
        
        strategy_summary = f"{active_strategies[0]}" if len(active_strategies) == 1 else f"Multiple ({len(active_strategies)})"
        coin_data = holdings_data.get(coin, {"usd": 0, "amt": 0})
        current_usd = coin_data["usd"]
        coin_amt = coin_data["amt"]

        if current_usd <= 0 and coin_amt <= 0:
            continue

        strategy_summary = f"{active_strategies[0]}" if len(active_strategies) == 1 else f"Multiple ({len(active_strategies)})"
        with st.expander(f"🪙 {coin} — ${current_usd:,.2f} ({coin_amt} {coin}) — Strategy: {strategy_summary}"):
            strategy_live_values = {}
            strategy_states = load_coin_state(user_id, coin, token, mode) or {}
            for strat in strategy_options:
                strat_info = strategy_states.get(strat, {})
                amount = strat_info.get("amount", 0)
                strategy_live_values[strat] = round(amount * prices.get(coin, 0), 2)

            strat_data = []
            for strat, alloc in allocations.items():
                active = alloc > 0
                live_value = strategy_live_values.get(strat, 0)
                status = "Inactive" if alloc == 0 else ("Holding" if live_value > 0 else "Waiting")
                strat_data.append({
                    "Strategy": strat,
                    "Value (Live USD)": f"${live_value:,.2f}",
                    "Active": "✅" if active else "❌",
                    "Status": status
                })
            df = pd.DataFrame(strat_data).set_index("Strategy")
            st.table(df)

            # Strategy Toggles
            toggle_cols = st.columns(len(strategy_options))
            for idx, strategy in enumerate(strategy_options):
                with toggle_cols[idx]:
                    toggle_key = f"{coin}_{strategy}_toggle"
                    active = allocations.get(strategy, {}).get("allocation", 0) > 0
                    new_state = st.checkbox(strategy, value=active, key=toggle_key)
                    if new_state != active:
                        allocations[strategy] = 1 if new_state else 0
                        st.session_state.pending_strategy_changes[coin] = True
                    if strategy != "HODL" and allocations[strategy] > 0:
                        profit_flag_key = f"{coin}_{strategy}_profit_only"
                        st.session_state.sell_only_profit_flags[coin][strategy] = st.checkbox(
                            "Sell only in profit?", 
                            value=st.session_state.sell_only_profit_flags[coin][strategy], 
                            key=profit_flag_key
                        )

            st.markdown("---")
            active_allocs = {s: a["allocation"] for s, a in allocations.items() if isinstance(a, dict) and a.get("allocation", 0) > 0}
            total_alloc = sum(active_allocs.values())

            slider_cols = st.columns(len(active_allocs) + 1)
            for idx, (strategy, value) in enumerate(active_allocs.items()):
                with slider_cols[idx]:
                    max_allowed = 100 - (total_alloc - value)
                    alloc_pct = st.slider(
                        label=f"{strategy} Allocation",
                        min_value=0,
                        max_value=int(max_allowed),
                        value=value,
                        key=f"{coin}_{strategy}_slider"
                    )
                    if alloc_pct != allocations[strategy]["allocation"]:
                        allocations[strategy]["allocation"] = alloc_pct
                        st.session_state.pending_strategy_changes[coin] = True
                    st.markdown(f"`{alloc_pct}%` — Allocated: `${(alloc_pct / 100) * current_usd:,.2f}`")

            with slider_cols[-1]:
                if active_allocs:
                    fig, ax = plt.subplots()
                    ax.pie(list(active_allocs.values()), labels=list(active_allocs.keys()), startangle=90, autopct='%1.1f%%')
                    ax.axis('equal')
                    st.pyplot(fig)

            if pending_change:
                st.warning("Changes detected. Save your strategy allocation?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Confirm {coin} Strategy Allocation"):
                        if sum(allocations.values()) != 100:
                            st.error("Allocations must equal 100%")
                        else:
                            save_strategy_state(coin, allocations, user_id, token, mode)
                            save_full_strategy_breakdown(coin, allocations, coin_amt, current_usd, user_id, token, mode)
                            st.session_state.pending_strategy_changes[coin] = False
                            st.success(f"{coin} strategy updated.")
                            st.rerun()
                with col2:
                    if st.button(f"❌ Cancel {coin} Changes"):
                        st.session_state.strategy_allocations[coin] = load_strategy_state(coin, strategy_options, user_id, token, mode)
                        st.session_state.pending_strategy_changes[coin] = False
                        st.rerun()

    st.divider()
    st.success("✅ Strategy Controls loaded.")
