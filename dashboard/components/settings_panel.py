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
    
    user_info = st.session_state.user
    role = user.get("role", "lead")
    is_paid_user = role in ["admin", "customer"]
    plan_code = user_info.get("plan", None)
    
    if is_paid_user and plan_code:
        if plan_code == "pro_month":
            plan_name = "Pro – $24.99/mo"
        elif plan_code == "pro_annual":
            plan_name = "Pro Annual – $149.99/yr"
        else:
            plan_name = "Pro Plan"
        st.success(f"✅ Current Plan: {plan_name}")
    else:
        st.warning("🚫 Current Plan: Free Version")
        if st.button("🚀 Upgrade to Pro", key="upgrade_button_settings_panel"):
            st.session_state.current_page = "checkout"
            st.rerun()
        return

    st.markdown("---")
    st.subheader("🔐 Exchange API Keys")

    exchange_options = ["kraken", "binance", "coinbase"]
    selected_exchange = st.selectbox("Select Exchange", exchange_options, index=exchange_options.index(exchange))

    current_keys = load_user_api_keys(user_id, selected_exchange, token=token)

    if "api_keys_saved" not in st.session_state:
        st.session_state.api_keys_saved = bool(current_keys)

    if st.session_state.api_keys_saved:
        st.success("✅ API keys already saved.")
        if st.button("✏️ Edit API Keys"):
            st.session_state.api_keys_saved = False
            st.rerun()
        return

    st.markdown(f"**Status:** {'✅ Keys saved' if current_keys else '❌ No keys saved'}")
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
