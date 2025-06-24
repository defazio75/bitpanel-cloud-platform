import streamlit as st
from utils.kraken_wrapper import get_prices
from utils.trade_simulator import simulate_trade
from utils.trade_executor import execute_trade
from utils.firebase_db import load_portfolio_snapshot
from utils.config import get_mode

def render_manual_trade_checkout(mode, user_id, token):
    st.title("🧾 Confirm Trade")

    # Load required session data
    selected_coin = st.session_state.get("selected_coin")
    trade_action = st.session_state.get("trade_action")

    if not all([selected_coin, trade_action]):
        st.error("❌ Missing session data. Please start from the Manual Trade page.")
        st.stop()

    # Load price and balance info
    prices = get_prices(user_id=user_id)
    coin_price = prices.get(selected_coin, 0)

    st.subheader(f"{trade_action.title()} {selected_coin}")

    # Input block
    col1, col2 = st.columns([3, 1])

    with col1:
        amount_usd = st.number_input(
            f"Amount to {trade_action.title()} (USD)",
            min_value=0.0,
            step=1.0,
            format="%.2f",
            key="trade_usd_amount"
        )

    with col2:
        if st.button("Max"):
            # Set max value based on mock placeholder; adjust to real balance lookup
            max_usd = 1000.0  # Placeholder
            st.session_state.trade_usd_amount = max_usd
            amount_usd = max_usd

    # Estimate
    if coin_price > 0 and amount_usd > 0:
        est_qty = round(amount_usd / coin_price, 6)
        st.markdown(f"**Estimated: {est_qty} {selected_coin} @ ${coin_price:.2f}**")
    else:
        est_qty = 0.0

    # Confirm trade
    if st.button("✅ Confirm Order"):
        if est_qty <= 0:
            st.error("❌ Invalid trade quantity.")
        else:
            try:
                if mode == "paper":
                    simulate_trade(
                        bot_name="ManualTrade",
                        action=trade_action,
                        amount=est_qty,
                        price=coin_price,
                        mode=mode,
                        coin=selected_coin,
                        user_id=user_id,
                        token=token
                    )
                else:
                    execute_trade(
                        bot_name="ManualTrade",
                        action=trade_action,
                        amount=est_qty,
                        price=coin_price,
                        mode=mode,
                        coin=selected_coin,
                        user_id=user_id
                    )
                st.success(f"✅ {trade_action.title()} {est_qty} {selected_coin} @ ${coin_price:.2f} successful.")

                # Redirect to Portfolio page after short pause
                st.session_state.page = "📊 Portfolio"
                st.rerun()

            except Exception as e:
                st.error(f"❌ Trade failed: {e}")
