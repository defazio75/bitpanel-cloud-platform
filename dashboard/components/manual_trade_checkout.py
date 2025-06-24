import streamlit as st
from utils.kraken_wrapper import get_prices
from utils.trade_simulator import simulate_trade
from utils.trade_executor import execute_trade
from utils.firebase_db import load_portfolio_snapshot
from utils.config import get_mode

def render_manual_trade_checkout(user_id, token, mode=None):
    st.title("✅ Confirm Manual Trade")

    # Load session state values
    selected_coin = st.session_state.get("trade_coin")
    action = st.session_state.get("trade_action")

    if not selected_coin or not action:
        st.error("❌ Trade information is missing. Please return to the Manual Trade page.")
        return

    if mode is None:
        mode = get_mode(user_id)

    # Load balances and prices
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    prices = get_prices(user_id=user_id)

    usd_balance = snapshot.get("usd_balance", 0.0)
    coin_info = snapshot.get("coins", {}).get(selected_coin, {})
    coin_balance = coin_info.get("balance", 0.0)
    price = prices.get(selected_coin, 0.0)

    # Determine max limit
    if action == "buy":
        max_usd = usd_balance
    else:
        max_usd = round(coin_balance * price, 2)

    st.subheader(f"{action.title()} {selected_coin}")

    col1, col2 = st.columns([3, 1])
    with col1:
        amount_usd = st.number_input(
            f"Amount to {action.title()} (USD)",
            min_value=0.0,
            max_value=max_usd,
            value=0.0,
            step=1.0,
            format="%.2f",
            key="manual_trade_amount"
        )
    with col2:
        if st.button("Max"):
            st.session_state.manual_trade_amount = max_usd
            st.rerun()

    qty = round(st.session_state.get("manual_trade_amount", 0.0) / price, 6) if price > 0 else 0.0
    st.write(f"Estimated: **{qty} {selected_coin}** at ${price:.2f}")

    if st.button(f"🚀 Confirm {action.title()} {selected_coin}"):
        if amount_usd <= 0:
            st.error("❌ Please enter an amount greater than 0.")
        elif price <= 0:
            st.error("❌ Invalid price. Please refresh and try again.")
        else:
            try:
                if mode == "paper":
                    simulate_trade(
                        bot_name="ManualTrade",
                        action=action,
                        amount=qty,
                        price=price,
                        mode=mode,
                        coin=selected_coin,
                        user_id=user_id,
                        token=token
                    )
                else:
                    execute_trade(
                        bot_name="ManualTrade",
                        action=action,
                        amount=qty,
                        price=price,
                        mode=mode,
                        coin=selected_coin,
                        user_id=user_id
                    )
                st.success(f"✅ {action.title()}ed {qty:.6f} {selected_coin} at ${price:.2f}")
                st.session_state.pop("manual_trade_amount", None)
                st.session_state.pop("trade_coin", None)
                st.session_state.pop("trade_action", None)
            except Exception as e:
                st.error(f"❌ Trade failed: {e}")
