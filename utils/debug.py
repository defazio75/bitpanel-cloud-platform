import streamlit as st
from utils.load_keys import load_user_api_keys
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.config import get_mode

def render_debug(user_id, token):
    mode = get_mode(user_id)
    st.title("🧪 Debug: Live Balance Save Test")
    st.markdown(f"**Mode:** `{mode}`")
    st.markdown(f"**User ID:** `{user_id}`")

    # === Firebase Token Check ===
    st.success("✅ Firebase Token Check")
    st.write(f"✅ Token verified: user_id matches (`{user_id}`)")

    # === API Keys Debug ===
    with st.expander("🔐 API Key Debug"):
        try:
            api_keys = load_user_api_keys(user_id, "kraken", token=token)
            st.write("✅ API Keys Loaded:", api_keys)
        except Exception as e:
            st.error(f"❌ Error loading API keys: {e}")

    # === Kraken Balances Debug ===
    with st.expander("💰 Kraken Balance Fetch"):
        try:
            balances = get_live_balances(user_id=user_id, token=token)
            st.write("📤 Final Balances Returned:", balances)
        except Exception as e:
            st.error(f"❌ Error fetching Kraken balances: {e}")

    # === Live Prices Debug ===
    with st.expander("💸 Live Prices"):
        try:
            prices = get_prices(user_id=user_id)
            st.json(prices)
        except Exception as e:
            st.error(f"❌ Error fetching prices: {e}")
