import streamlit as st
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.config import get_mode

def render_debug(user_id, token):
    mode = get_mode(user_id)
    st.title("🧪 Live Kraken Debug")

    st.markdown(f"**Mode:** `{mode}`")

    try:
        balances = get_live_balances(user_id=user_id, token=token)
        prices = get_prices(user_id=user_id)

        st.write("💰 Live Balances from Kraken:", balances)
        st.write("📈 Live Prices from Kraken:", prices)
    except Exception as e:
        st.error(f"❌ Error fetching data: {e}")
