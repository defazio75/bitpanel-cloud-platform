import streamlit as st
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.config import get_mode

def render_debug(user_id, token):
    mode = get_mode(user_id)

    st.title("🧪 Live Kraken Debug")

    balances = get_live_balances(user_id=user_id, token=token)
    prices = get_prices(user_id=user_id)

    st.write("💰 Live Balances:", balances)
    st.write("📈 Live Prices:", prices)
