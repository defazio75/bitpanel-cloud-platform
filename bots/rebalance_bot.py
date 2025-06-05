from datetime import datetime
from utils.kraken_wrapper import get_prices
from utils.config import get_mode
import streamlit as st
from utils.firebase_db import (
    load_coin_state,
    load_portfolio_snapshot,
)

def rebalance_hodl(user_id, mode, token):
    print(f"[Rebalance HODL] Running in {mode.upper()} mode...")

    if mode == "live":
        from utils.trade_executor import execute_trade
    else:
        from utils.trade_simulator import simulate_trade as execute_trade

    token = st.session_state.user["token"]
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    if not snapshot:
        print("❌ portfolio_snapshot not found.")
        return

    prices = get_prices(user_id=user_id)
    coins = snapshot.get("coins", {})

    for coin, data in coins.items():
        price = prices.get(coin.upper())
        if not price:
            continue

        # Load coin strategy state
        state = load_coin_state(user_id, coin, token, mode)
        hodl = state.get("HODL", {})
        target_amt = hodl.get("amount", 0)
        snapshot_amt = data.get("balance", 0)

        delta = round(target_amt - snapshot_amt, 8)
        if abs(delta * price) < 1:
            continue

        action = "buy" if delta > 0 else "sell"
        print(f"{action.upper()} {abs(delta)} {coin} to match HODL target of {target_amt}")
            
        # Execute the trade to align with target allocation
        execute_trade(
            user_id=user_id,
            bot_name="rebalance_hodl",
            action=action,
            amount=abs(new_balance - current_balance),
            price=current_price,
            mode=mode,
            coin=coin
        )

    print("✅ Rebalancing complete.")
