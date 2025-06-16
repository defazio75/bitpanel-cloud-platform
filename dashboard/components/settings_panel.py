import streamlit as st
import stripe
from utils.firebase_db import save_user_api_keys
from utils.load_keys import load_user_api_keys
import streamlit.components.v1 as components

stripe.api_key = "sk_test_..."  # your full key

PLAN_LOOKUP = {
    "Starter - $9/mo": "price_...",
    "Pro - $25/mo": "price_...",
    "Pro Annual - $149/yr": "price_..."
}

def render_settings_panel(user_id, token, exchange="kraken"):
    st.header("⚙️ Settings")

    # === Account Info ===
    st.subheader("👤 Account Info")
    user = st.session_state.get("user", {})
    st.write(f"**Email:** {user.get('email', 'N/A')}")
    st.write(f"**User ID:** {user_id}")
    st.markdown("---")

    # === Subscription Plan ===
    st.subheader("💳 Subscription Plan (Includes 30-Day Free Trial 🚀)")
    st.markdown("✅ No payment for 30 days. Cancel anytime.")

    plans = list(PLAN_LOOKUP.keys())

    if "selected_plan" not in st.session_state:
        st.session_state.selected_plan = None
    if "stripe_session_url" not in st.session_state:
        st.session_state.stripe_session_url = None

    cols = st.columns(len(plans))
    for i, plan in enumerate(plans):
        with cols[i]:
            if st.button(plan):
                st.session_state.selected_plan = plan
                st.session_state.stripe_session_url = None

    if st.session_state.selected_plan:
        st.markdown(f"**Selected Plan:** `{st.session_state.selected_plan}`")

        if st.button("🚀 Sign Up for Free Trial"):
            try:
                price_id = PLAN_LOOKUP[st.session_state.selected_plan]
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    mode="subscription",
                    line_items=[{"price": price_id, "quantity": 1}],
                    subscription_data={
                        "trial_period_days": 30,
                        "metadata": {"user_id": user_id}
                    },
                    success_url="https://yourapp.com/success",
                    cancel_url="https://yourapp.com/cancel",
                    metadata={"user_id": user_id}
                )
                st.session_state.stripe_session_url = session.url
            except Exception as e:
                st.error(f"❌ Error creating Stripe session: {e}")

    if st.session_state.stripe_session_url:
        st.markdown(
            f"➡️ [Continue to Stripe to activate your 30-day free trial]({st.session_state.stripe_session_url})",
            unsafe_allow_html=True
        )

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
