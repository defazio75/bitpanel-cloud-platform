import streamlit as st
from datetime import datetime

from utils.kraken_wrapper import get_live_balances, get_prices
from utils.firebase_db import save_portfolio_snapshot
from utils.config import get_mode
from utils.load_keys import load_user_api_keys
from utils.kraken_auth import rate_limited_query_private


def render_debug():
    st.title("🚀 BitPanel")

    # === Get user info from session ===
    user = st.session_state.get("user", {})
    user_id = user.get("localId")
    token = user.get("token")

    if not user_id or not token:
        st.error("❌ Missing user_id or token. Please log in.")
        return

    mode = get_mode(user_id)
    st.markdown(f"**Current Mode:** `{mode}`")

    # === Load API Keys ===
    exchange = "kraken"
    keys = load_user_api_keys(user_id, exchange, token=token)

    st.subheader("🔐 Loaded API Keys")
    if keys:
        st.json(keys)
    else:
        st.error("❌ No Kraken API keys found for this user.")
        return

    # === Test direct Kraken balance call ===
    st.subheader("📡 Raw Kraken Balance API Test")
    try:
        raw_result = rate_limited_query_private("/0/private/Balance", {}, user_id, token)
        st.success("✅ Kraken API balance call successful!")
        st.json(raw_result)
    except Exception as e:
        st.error(f"❌ Error calling Kraken Balance API directly: {e}")
        return

    # === Get balances and prices using wrapper ===
    st.subheader("🔁 Live Kraken Balances (via wrapper)")
    balances = get_live_balances(user_id=user_id, token=token)
    st.write(balances)

    st.subheader("💰 Current Prices")
    prices = get_prices(user_id=user_id)
    st.write(prices)

    # === Build snapshot ===
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

    # === Save button ===
    if st.button("🚀 Save Snapshot to Firebase"):
        save_portfolio_snapshot(user_id=user_id, snapshot=snapshot, token=token, mode=mode)
        st.success("✅ Snapshot saved.")
