import streamlit as st

SUPPORTED_COINS = ["BTC", "ETH", "SOL", "XRP", "LINK", "DOT"]

def render_manual_trade(mode, user_id, token):
    st.title("\U0001F4B8 Manual Trade")
    st.caption("Select a coin and whether you want to Buy or Sell. You'll confirm the order on the next page.")

    # Trade Entry Panel
    st.markdown("### \U0001F4E6 Trade Selection")

    selected_coin = st.selectbox("Select a Coin", ["-- No Coin Selected --"] + SUPPORTED_COINS, key="coin_selector")

    if selected_coin and selected_coin != "-- No Coin Selected --":
        st.markdown(f"#### Selected Coin: {selected_coin}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Buy {selected_coin}", key="buy_button"):
                st.session_state.selected_coin = selected_coin
                st.session_state.trade_action = "buy"
                st.session_state.page = "manual_trade_checkout"
                st.rerun()

        with col2:
            if st.button(f"Sell {selected_coin}", key="sell_button"):
                st.session_state.selected_coin = selected_coin
                st.session_state.trade_action = "sell"
                st.session_state.page = "manual_trade_checkout"
                st.rerun()
