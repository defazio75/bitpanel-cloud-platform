import streamlit as st
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.firebase_db import save_live_snapshot_from_kraken
from utils.firebase_config import firebase
from utils.firebase_auth import auth
from datetime import datetime

def render_debug(user_id, token, mode="live"):
    st.title("🧪 Debug: Live Balance Save Test")

    st.markdown(f"**Mode:** `{mode}`")
    st.markdown(f"**User ID:** `{user_id}`")

    # === Step 1: Verify token matches user_id ===
    st.subheader("✅ Firebase Token Check")
    try:
        resolved_uid = auth.get_account_info(token)["users"][0]["localId"]
        if resolved_uid != user_id:
            st.error(f"❌ Token mismatch: token belongs to {resolved_uid}, but current user_id is {user_id}")
            return
        st.success(f"✅ Token verified: user_id matches ({resolved_uid})")
    except Exception as e:
        st.error("❌ Failed to verify token with Firebase Auth.")
        st.exception(e)
        return

    # === Step 2: Pull live balances ===
    st.subheader("💰 Kraken Balances")
    try:
        balances = get_live_balances(user_id=user_id, token=token)
        st.json(balances)
    except Exception as e:
        st.error("❌ Error pulling balances from Kraken.")
        st.exception(e)
        return

    # === Step 3: Pull live prices ===
    st.subheader("💸 Live Prices (USD)")
    try:
        prices = get_prices(user_id=user_id)
        st.json(prices)
    except Exception as e:
        st.error("❌ Error fetching live prices.")
        st.exception(e)
        return

    # === Step 4: Build snapshot manually for preview ===
    st.subheader("📦 Snapshot to Be Saved")
    try:
        coins = {}
        usd_balance = float(balances.get("USD", 0.0))
        total_value = usd_balance
        tracked = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]

        for symbol in tracked:
            amount = float(balances.get(symbol, 0.0))
            price = prices.get(symbol, 0.0)
            usd_value = round(amount * price, 2)

            coins[symbol] = {
                "balance": round(amount, 8),
                "usd_value": usd_value
            }

            total_value += usd_value

        snapshot = {
            "usd_balance": round(usd_balance, 2),
            "coins": coins,
            "timestamp": datetime.utcnow().isoformat(),
            "total_value": round(total_value, 2)
        }

        st.json(snapshot)
    except Exception as e:
        st.error("❌ Failed to build snapshot.")
        st.exception(e)
        return

    # === Step 5: Attempt to save to Firebase ===
    st.subheader("📤 Attempting Firebase Save")

    try:
        firebase.database() \
            .child("users") \
            .child(user_id) \
            .child(mode) \
            .child("balances") \
            .child("portfolio_snapshot") \
            .set(snapshot, token)
        st.success("✅ Snapshot successfully saved to Firebase!")
    except Exception as e:
        st.error("❌ Firebase write failed.")
        st.exception(e)
