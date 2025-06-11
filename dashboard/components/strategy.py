import streamlit as st
from utils.firebase_db import load_strategy_allocations, save_strategy_allocations, load_portfolio_snapshot
from utils.config import get_mode

# === Constants ===
MARKET_ASSUMPTIONS = ["Bullish", "Neutral", "Bearish", "Custom"]
STRATEGIES = ["HODL", "5min RSI", "1hr RSI", "DCA Matrix", "Bollinger"]

# === Render Strategy Allocation ===
def render_strategy_controls(mode, user_id, token):
    st.title("🧠 Strategy Controls")
    st.caption(f"Mode: `{mode.upper()}`")

    # Load user portfolio and filter coins with non-zero balances
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    portfolio_coins = snapshot.get("coins", {})
    coins = [coin for coin, data in portfolio_coins.items() if data.get("balance", 0) > 0]

    # Initialize strategy data
    strategy_data = load_strategy_allocations(user_id, token, mode) or {}

    for coin in COINS:
        st.subheader(f"{coin} Strategy")

        # Market assumption selector
        default_assumption = strategy_data.get(coin, {}).get("assumption", "Neutral")
        assumption = st.radio(
            f"Market View for {coin}",
            MARKET_ASSUMPTIONS,
            horizontal=True,
            key=f"{coin}_assumption",
            index=MARKET_ASSUMPTIONS.index(default_assumption)
        )

        sliders = {}
        if assumption == "Custom":
            st.markdown("**Custom Allocation**")
            total_alloc = 0
            for strat in STRATEGIES:
                val = st.slider(
                    f"{strat} Allocation %",
                    0, 100,
                    strategy_data.get(coin, {}).get(strat, 0),
                    key=f"{coin}_{strat}"
                )
                sliders[strat] = val
                total_alloc += val

            if total_alloc != 100:
                st.warning(f"⚠️ {coin}: Strategy allocation must total 100% (Current: {total_alloc}%)")

        # Save button
        if st.button(f"💾 Save {coin} Strategy", key=f"save_{coin}"):
            if assumption == "Custom" and total_alloc != 100:
                st.error("❌ Allocation must total 100% before saving.")
            else:
                updated = {"assumption": assumption}
                if assumption == "Custom":
                    updated.update(sliders)
                save_strategy_allocations(user_id, coin, updated, mode, token)
                st.success("✅ Strategy saved.")

        st.divider()
