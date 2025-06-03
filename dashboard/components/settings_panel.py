import streamlit as st
from utils.firebase_db import save_user_api_keys
from utils.load_keys import load_user_api_keys
from utils.kraken_wrapper import get_live_balances

def test_kraken_balance_fetch(user_id):
    try:
        balances = get_live_balances(user_id=user_id)
        usd = balances.get("USD", 0)
        print(f"✅ USD Balance from Kraken for {user_id}: ${usd}")
        return usd
    except Exception as e:
        print(f"❌ Test Fetch Failed: {e}")
        return None

def render_settings_panel(user_id, token, exchange="kraken"):
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

    current_keys = load_user_api_keys(user_id, selected_exchange, token=token)

    if "api_keys_saved" not in st.session_state:
         st.session_state.api_keys_saved = False

    if st.session_state.api_keys_saved:
        st.success("✅ API keys already saved.")
        if st.button("✏️ Edit API Keys"):
            st.session_state.api_keys_saved = False
            st.experimental_rerun()
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
                st.experimental_rerun()
            else:
                st.error("Please enter both API key and secret.")

    st.markdown("---")

    # === Test Kraken Connection Section ===
    st.subheader("🧪 Test Kraken Connection")

    if st.button("🔍 Test Kraken Balance Fetch"):
        balances = get_live_balances(user_id=user_id)

        if balances:
            st.write("🧾 **Raw Kraken Balances:**")
            st.json(balances)
            usd_balance = balances.get("USD", 0)
            st.success(f"✅ USD Balance: ${usd_balance:.2f}")
        else:
            st.error("❌ No balances returned. Check API key validity or Kraken API access.")

    st.markdown("---")
    st.markdown("Future settings like subscriptions and theme preferences will be added here.")
