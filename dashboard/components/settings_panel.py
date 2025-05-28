import streamlit as st
from utils.api_keys import load_api_keys, save_api_keys, get_api_key_path
import os

def render_settings_panel(user_id, exchange="kraken"):
    st.header("⚙️ Settings")

    # === Account Info ===
    st.subheader("👤 Account Info")
    user = st.session_state.get("user", {})
    st.write(f"**Email:** {user.get('email', 'N/A')}")
    st.write(f"**User ID:** {user_id}")

    st.markdown("---")

    # === API Key Manager ===
    st.subheader("🔐 Exchange API Keys")

    exchange_options = ["kraken", "binance", "coinbase"]
    selected_exchange = st.selectbox("Select Exchange", exchange_options, index=exchange_options.index(exchange))

    current_keys = load_api_keys(user_id, selected_exchange)
    key_status = "✅ Keys saved" if current_keys else "❌ No keys saved"
    st.markdown(f"**Status:** {key_status}")

    st.markdown("You can safely store or update your API keys below. These are kept securely and never shared.")

    with st.form(f"api_key_form_{selected_exchange}"):
        new_key = st.text_input(f"{selected_exchange.capitalize()} API Key", type="default")
        new_secret = st.text_input(f"{selected_exchange.capitalize()} API Secret", type="password")
        submit = st.form_submit_button("💾 Save API Keys")

        if submit:
            if new_key and new_secret:
                save_api_keys(user_id, selected_exchange, new_key, new_secret)
                st.success("✅ API keys saved successfully.")
                st.experimental_rerun()
            else:
                st.error("Please enter both API key and secret.")

    # Delete Keys Option
    if current_keys:
        if st.button("🗑️ Delete Saved API Keys"):
            key_path = get_api_key_path(user_id, selected_exchange)
            if os.path.exists(key_path):
                os.remove(key_path)
                st.success("🚫 API keys deleted.")
                st.experimental_rerun()

    st.markdown("---")
    st.markdown("Future settings like subscriptions and theme preferences will be added here.")
