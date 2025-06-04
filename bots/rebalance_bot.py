from datetime import datetime
from utils.kraken_wrapper import get_prices
from utils.config import get_mode
import streamlit as st
from utils.firebase_db import (
    load_coin_state,
    save_coin_state,
    load_portfolio_snapshot,
    save_portfolio_snapshot
)

def rebalance_hodl(user_id, mode, token):
    print(f"[Rebalance HODL] Running in {mode.upper()} mode...")

    if mode == "live":
        from utils.trade_executor import execute_trade
    else:
        from utils.trade_simulator import simulate_trade as execute_trade

    token = st.session_state.user["token"]

    # === Load snapshot
    current_snapshot = load_portfolio_snapshot(user_id, token, mode)
    if not current_snapshot:
        print("❌ portfolio_snapshot.json not found.")
        return

    prices = get_prices(user_id=user_id)
    usd_balance = current_snapshot.get("usd_balance", 0)
    updated_coins = {}

    coin_list = current_snapshot.get("coins", {}).keys()

    for coin in coin_list:
        state = load_coin_state(user_id, coin, token, mode)
        if not state or "target_usd" not in state:
            continue  # skip coins without HODL targets

        target_usd = state["target_usd"]
        current_price = prices.get(coin, 0)
        coin_data = current_snapshot["coins"].get(coin, {"balance": 0})
        current_balance = coin_data.get("balance", 0)
        current_value = current_balance * current_price

        delta = round(target_usd - current_value, 2)
        if abs(delta) < 1 or current_price == 0:
            continue

        side = "buy" if delta > 0 else "sell"
        trade_usd = abs(delta)
        coin_amount = trade_usd / current_price

        if side == "sell" and usd_balance >= target_usd:
            print(f"💡 Skipping {coin} sell — already have ${usd_balance} available")
            continue

        print(f"{side.upper()} ${trade_usd} of {coin} at ${current_price:.2f}")

        # === Pre-trade calculations (safe before execution)
        new_balance = round(target_usd / current_price, 8)
        usd_diff = round((new_balance - current_balance) * current_price, 2)


        # Determine buy/sell action
        if usd_diff > 0:
            usd_balance -= usd_diff
            action = "buy"
        else:
            usd_balance += abs(usd_diff)
            action = "sell"
            
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
        
        # Overwrite the new balance in snapshot
        current_snapshot["coins"][coin] = {
            "balance": new_balance,
            "price": current_price,
            "value": round(new_balance * current_price, 2)
        }

        # Update HODL state
        state.update({
            "status": "Holding",
            "amount": new_balance,
            "buy_price": current_price,
            "timestamp": datetime.utcnow().isoformat()
        })
        save_coin_state(user_id, coin, state, token, mode)

    # === Final snapshot update
    current_snapshot["usd_balance"] = round(usd_balance, 2)
    current_snapshot["timestamp"] = datetime.utcnow().isoformat()
    coins_data = current_snapshot.get("coins", {})
    current_snapshot["total_value"] = round(
        usd_balance + sum(c.get("balance", 0) * c.get("price", 0) for c in coins_data.values()), 2
    )
    save_portfolio_snapshot(user_id, current_snapshot, token, mode)

    print("✅ Rebalancing complete.")
