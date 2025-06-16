import streamlit as st
import stripe
from utils.firebase_db import save_user_api_keys
from utils.load_keys import load_user_api_keys
import streamlit.components.v1 as components

stripe.api_key = "sk_test_51RaeXf2cME1qYwWKSuTCtxpAPbWr8dZcUQSzOUFaxnf2BWAKl26O6kPqKMLXnF66dPMdgjPbsF3jywwtqXJqoogX00rv5AUFEj" 

PLAN_LOOKUP = {
    "Pro – $24.99/mo": "price_1Raedr2cME1qYwWKk4onb9Tw",
    "Pro Annual – $149.99/yr": "price_1RakiW2cME1qYwWKwhyZv8BP"
}

PLAN_DETAILS = {
    "Pro – $24.99/mo": [
        "✅ Full Access to All Bots",
        "✅ Live + Paper Trading",
        "✅ Supports BTC, ETH, XRP, DOT, LINK, SOL",
        "✅ Supports All Coins",
        "✅ Connect with Coinbase, Binance, or Kraken",
        "✅ Cancel Anytime"
    ],
    "Pro Annual – $149.99/yr": [
        "✅ Everything in Pro Plan",
        "✅ Save 50% vs Monthly",
        "✅ Priority Feature Access",
        "✅ Cancel Anytime"
    ]
}

def render_settings_panel(user_id, token, exchange="kraken"):
    st.header("⚙️ Settings")

    # === Account Info ===
    st.subheader("👤 Account Info")
    user = st.session_state.get("user", {})
    st.write(f"**Email:** {user.get('email', 'N/A')}")
    st.write(f"**User ID:** {user_id}")
    st.markdown("---")

    # === Subscription Section ===
    st.subheader("💳 Subscription Plan")
    
    is_paid_user = st.session_state.user.get("paid", False)
    
    if is_paid_user:
        plan_name = st.session_state.user.get("plan_name", "Pro Plan")  # Optional: customize
        st.success(f"✅ Current Plan: {plan_name}")
    else:
        st.warning("🚫 Current Plan: Free Version")
        if st.button("🚀 Upgrade to Pro"):
            webbrowser.open_new_tab("/checkout")

    st.markdown("---")
    st.subheader("🔐 Exchange API Keys")

    exchange_options = ["kraken", "binance", "coinbase"]
    selected_exchange = st.selectbox("Select Exchange", exchange_options, index=exchange_options.index(exchange))

    current_keys = load_user_api_keys(user_id, selected_exchange, token=token)

    if "api_keys_saved" not in st.session_state:
        st.session_state.api_keys_saved = False

    if st.session_state.api_keys_saved:
        st.success("✅ API keys already saved.")
        if st.button("✏️ Edit API Keys"):
            st.session_state.api_keys_saved = False
            st.rerun()
        return

    key_status = "✅ Keys saved" if current_keys else "❌ No keys saved"
    st.markdown(f"**Status:** {key_status}")
    st.markdown("You can safely store or update your API keys below. These are encrypted and saved securely.")

    with st.form(f"api_key_form_{selected_exchange}"):
        new_key = st.text_input(f"{selected_exchange.capitalize()} API Key", type="default")
        new_secret = st.text_input(f"{selected_exchange.capitalize()} API Secret", type="password")
        submit = st.form_submit_button("💾 Save API Keys")

        if submit:
            if new_key and new_secret:
                save_user_api_keys(user_id, selected_exchange, new_key, new_secret, token=token)
                st.success("✅ API keys saved successfully.")
                st.session_state.api_keys_saved = True
                st.rerun()
            else:
                st.error("Please enter both API key and secret.")
