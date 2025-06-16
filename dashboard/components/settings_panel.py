import streamlit as st
import stripe
from utils.firebase_db import save_user_api_keys
from utils.load_keys import load_user_api_keys

stripe.api_key = "sk_test_51RaeXf2cME1qYwWKSuTCtxpAPbWr8dZcUQSzOUFaxnf2BWAKl26O6kPqKMLXnF66dPMdgjPbsF3jywwtqXJqoogX00rv5AUFEj"  

# Stripe Price IDs (set in Stripe Dashboard)
PLAN_LOOKUP = {
    "Starter - $9/mo": "prod_SVfzzUjlsDIvwU",
    "Pro - $25/mo": "prod_SVfzXVhlbyzof3",
    "Pro Annual - $149/yr": "prod_SVg0OppVq8zmLJ"
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

    plan = st.selectbox("Choose Your Plan", list(PLAN_LOOKUP.keys()))

    if st.button("Subscribe Now"):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{
                    "price": PLAN_LOOKUP[plan],
                    "quantity": 1,
                }],
                success_url="https://yourapp.com/success",
                cancel_url="https://yourapp.com/cancel",
                metadata={"user_id": user_id}
            )
            st.success("✅ Redirecting to Stripe Checkout...")
            st.markdown(f"[Click here to complete payment]({session.url})", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error creating Stripe session: {e}")

    st.markdown("---")

    # === API Key Manager ===
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

    st.markdown("---")
