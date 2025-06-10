import streamlit as st
from utils.load_keys import load_user_api_keys
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.config import get_mode

def render_debug(user_id, token):
    st.title("🧪 Kraken Live Snapshot Debug")

    mode = get_mode(user_id)
    st.markdown(f"**Mode:** `{mode}`")

    st.subheader("1️⃣ Testing `get_live_balances()`")
    try:
        balances = get_live_balances(user_id=user_id, token=token)
        st.json(balances)
    except Exception as e:
        st.error("❌ Failed to fetch live balances")
        st.exception(e)

    st.subheader("2️⃣ Testing `get_prices()`")
    try:
        prices = get_prices(user_id=user_id)
        st.json(prices)
    except Exception as e:
        st.error("❌ Failed to fetch prices")
        st.exception(e)

    st.subheader("3️⃣ Calling `save_live_snapshot_from_kraken()`")
    try:
        save_live_snapshot_from_kraken(user_id=user_id, token=token, mode=mode)
        st.success("✅ Snapshot save function executed.")
    except Exception as e:
        st.error("❌ Snapshot save function crashed.")
        st.exception(e)

    st.subheader("4️⃣ Verifying saved snapshot")
    try:
        refetch = firebase.database() \
            .child("users") \
            .child(user_id) \
            .child(mode) \
            .child("balances") \
            .child("portfolio_snapshot") \
            .get(token).val()

        if refetch:
            st.json(refetch)
        else:
            st.warning("⚠️ No portfolio_snapshot found in Firebase.")
    except Exception as e:
        st.error("❌ Could not fetch saved snapshot.")
        st.exception(e)

    st.subheader("5️⃣ Writing Firebase test key")
    try:
        firebase.database() \
            .child("users") \
            .child(user_id) \
            .child("test_snapshot_write") \
            .set({"status": "✅ live snapshot reached this point"}, token)

        st.success("✅ Test write to Firebase successful.")
    except Exception as e:
        st.error("❌ Test write to Firebase failed.")
        st.exception(e)
