import streamlit as st
import sys
import os
from datetime import datetime

from utils.kraken_wrapper import get_prices
from utils.firebase_db import load_portfolio_snapshot
from utils.trade_simulator import simulate_trade
from utils.trade_executor import execute_trade

def render_manual_trade(mode, user_id, token):
    st.title("💸 Manual Trade")
    st.caption("Manually buy or sell crypto using your available balance.")

    # Load balances and prices
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    prices = get_prices(user_id=user_id)

    usd_balance = snapshot.get("usd_balance", 0.0)
    coin_data = snapshot.get("coins", {})

    SUPPORTED_COINS = ["BTC", "ETH", "SOL", "XRP", "LINK", "DOT"]
    coins = {}

    for coin in SUPPORTED_COINS:
        balance = coin_data.get(coin, {}).get("balance", 0.0)
        price = prices.get(coin, 0.0)
        usd_value = round(balance * price, 2)
        coins[coin] = {
            "balance": balance,
            "price": price,
            "usd": usd_value
        }

    st.markdown(f"**💵 Available USD:** `${usd_balance:,.2f}``")

    with st.expander("🛒 Trade Now", expanded=True):
        selected_coin = st.selectbox("Select a Coin", SUPPORTED_COINS)
        coin_price = coins[selected_coin]["price"]
        coin_balance = coins[selected_coin]["balance"]
        coin_usd_value = coins[selected_coin]["usd"]

        col1, col2 = st.columns(2)

        # BUY section
        with col1:
            st.subheader("Buy")
            max_buy = usd_balance

            buy_amount = st.number_input(
                "Amount to Buy (USD)",
                min_value=0.0,
                max_value=max_buy,
                step=1.0,
                format="%.2f",
                key="buy_amount_input"
            )

            buy_qty = round(buy_amount / coin_price, 6) if coin_price > 0 else 0.0
            st.write(f"Estimated: **{buy_qty} {selected_coin}**")

            if st.button(f"Execute Buy {selected_coin}"):
                if buy_amount <= 0:
                    st.error("❌ Please enter USD amount greater than 0.")
                elif coin_price <= 0:
                    st.error(f"❌ Invalid price for {selected_coin}. Please refresh or try again later.")
                else:
                    try:
                        if mode == "paper":
                            simulate_trade(
                                bot_name="ManualTrade",
                                action="buy",
                                amount=buy_qty,
                                price=coin_price,
                                mode=mode,
                                coin=selected_coin,
                                user_id=user_id,
                                token=token
                            )
                        else:
                            execute_trade(
                                bot_name="ManualTrade",
                                action="buy",
                                amount=buy_qty,
                                price=coin_price,
                                mode=mode,
                                coin=selected_coin,
                                user_id=user_id
                            )
                        st.success(f"✅ Bought {buy_qty:.6f} {selected_coin} at ${coin_price:.2f}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Trade failed: {e}")
        # SELL section
        with col2:
            st.subheader("Sell")
            max_sell = coin_usd_value

            sell_amount = st.number_input(
                "Amount to Sell (USD)",
                min_value=0.0,
                max_value=max_sell,
                step=1.0,
                format="%.2f",
                key="sell_amount_input"
            )

            sell_qty = round(sell_amount / coin_price, 6) if coin_price > 0 else 0.0
            st.write(f"Estimated: **{sell_qty} {selected_coin}**")

            if st.button(f"Execute Sell {selected_coin}"):
                if sell_amount > 0:
                    if mode == "paper":
                        simulate_trade(
                            bot_name="ManualTrade",
                            action="sell",
                            amount=sell_qty,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id,
                            token=token
                        )
                    else:
                        execute_trade(
                            bot_name="ManualTrade",
                            action="sell",
                            amount=sell_qty,
                            price=coin_price,
                            mode=mode,
                            coin=selected_coin,
                            user_id=user_id
                        )
                    st.success(f"✅ Sold {sell_qty} {selected_coin} at ${coin_price:.2f}")
                    st.rerun()
