# dashboard/test_keys.py
import streamlit as st
from utils.firebase_db import load_user_api_keys

def run_key_test():
    user_id = st.session_state.user.get("user_id")
    exchange = "kraken"

    st.subheader("🔐 API Key Decryption Test")
    st.write(f"Testing decryption for user: `{user_id}`")

    try:
        keys = load_user_api_keys(user_id, exchange)
        st.success("✅ Keys decrypted successfully!")
        st.code(f"API Key: {keys.get('key')[:6]}...", language="text")
        st.code(f"API Secret: {keys.get('secret')[:6]}...", language="text")
    except Exception as e:
        st.error(f"❌ Error decrypting API keys: {e}")
