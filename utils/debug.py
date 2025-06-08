import streamlit as st
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.firebase_db import (
    load_portfolio_snapshot,
    save_live_snapshot_from_kraken
)
from utils.load_keys import load_user_api_keys
from utils.config import get_mode


def render_debug(user_id, token):
    mode = get_mode(user_id)
    st.title("🧪 BitPanel Debug Dashboard")
    st.markdown(f"**Mode:** `{mode}`")

    # === API Key Check ===
    st.subheader("🔐 Kraken API Key Status")
    try:
        keys = load_user_api_keys(user_id, "kraken", token)
        if keys.get("key") and keys.get("secret"):
            st.success("✅ Kraken API keys loaded successfully.")
        else:
            st.error("❌ API keys are missing or empty.")
    except Exception as e:
        st.error(f"❌ Failed to load API keys: {e}")
        return

    # === Fetch Live Balances and Prices ===
    st.subheader("📡 Kraken Live Data")
    try:
        balances = get_live_balances(user_id=user_id, token=token)
        prices = get_prices(user_id=user_id)

        st.write("💰 Kraken Balances:", balances)
        st.write("📈 Kraken Prices:", prices)

        if not balances or all(v == 0 for v in balances.values()):
            st.warning("⚠️ Balances appear to be empty or all zero.")
            st.markdown("Possible causes:")
            st.markdown("- ❌ Invalid API keys")
            st.markdown("- 🔒 Incomplete API permissions (must include 'Query Funds')")
            st.markdown("- 🪙 Zero assets in your Kraken account")
            st.markdown("- 🌐 Kraken API outage or error")
    except Exception as e:
        st.error(f"❌ Error fetching Kraken data: {e}")
        return

    # === Firebase Snapshot Display ===
    st.subheader("📦 Firebase Portfolio Snapshot")
    try:
        snapshot = load_portfolio_snapshot(user_id=user_id, token=token, mode=mode)
        st.write(snapshot)

        # Compare live USD vs saved USD
        usd_live = balances.get("USD", 0)
        usd_saved = snapshot.get("usd_balance", 0)
        st.metric("💵 USD in Kraken", f"${usd_live:,.2f}")
        st.metric("📄 USD in Firebase Snapshot", f"${usd_saved:,.2f}")
    except Exception as e:
        st.error(f"❌ Failed to load Firebase snapshot: {e}")

    # === Manual Snapshot Trigger ===
    st.subheader("🛠️ Manual Snapshot Test")
    if st.button("🔁 Re-Save Live Snapshot to Firebase"):
        try:
            save_live_snapshot_from_kraken(user_id=user_id, token=token, mode=mode)
            st.success("✅ Live snapshot saved successfully.")
        except Exception as e:
            st.error(f"❌ Failed to save snapshot: {e}")
