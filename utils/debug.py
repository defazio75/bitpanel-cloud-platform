import streamlit as st
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.firebase_db import save_portfolio_snapshot
from datetime import datetime
from utils.config import get_mode

def render_debug():
    user = st.session_state.get("user", {})
    user_id = user.get("id")
    token = user.get("token")

    if not user_id or not token:
        st.error("❌ Missing user_id or token. Please log in.")
        return

    mode = get_mode(user_id)
    st.markdown(f"**Current Mode:** `{mode}`")

    # === Get Kraken balances and prices
    balances = get_live_balances(user_id=user_id, token=token)
    prices = get_prices(user_id=user_id)

    st.subheader("🔁 Live Kraken Balances")
    st.write(balances)

    st.subheader("💰 Current Prices")
    st.write(prices)

    # === Build snapshot
    tracked = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]
    coins = {}
    usd_balance = float(balances.get("USD", 0.0))
    total_value = usd_balance

    for coin in tracked:
        amt = float(balances.get(coin, 0.0))
        price = float(prices.get(coin, 0.0))
        usd_val = round(amt * price, 2)
        coins[coin] = {
            "balance": round(amt, 8),
            "usd_value": usd_val
        }
        total_value += usd_val

    snapshot = {
        "usd_balance": round(usd_balance, 2),
        "coins": coins,
        "timestamp": datetime.utcnow().isoformat(),
        "total_value": round(total_value, 2)
    }

    st.subheader("📦 Snapshot Preview")
    st.write(snapshot)

    # === Save button
    if st.button("🚀 Save Snapshot to Firebase"):
        save_portfolio_snapshot(user_id=user_id, snapshot=snapshot, token=token, mode=mode)
        st.success("✅ Snapshot saved.")
