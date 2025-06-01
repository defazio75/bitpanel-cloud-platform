from datetime import datetime
from utils.kraken_wrapper import get_prices
from utils.config import get_mode
from utils.firebase_db import load_firebase_json, save_firebase_json
import streamlit as st

if mode == "live":
    from utils.trade_executor import execute_trade
else:
    from utils.trade_simulator import execute_trade

def rebalance_hodl(user_id):
    mode = get_mode(user_id=user_id)
    print(f"[Rebalance HODL] Running in {mode.upper()} mode...")

    token = st.session_state.user["token"]

    # === Load snapshot
    snapshot_path = f"{mode}/balances/portfolio_snapshot.json"
    current_snapshot = load_firebase_json(snapshot_path, user_id, token)

    if not current_snapshot:
        print("❌ portfolio_snapshot.json not found.")
        return

    prices = get_prices(user_id=user_id)
    usd_balance = current_snapshot.get("usd_balance", 0)
    updated_coins = {}

    coin_list = current_snapshot.get("coins", {}).keys()

    for coin in coin_list:
        state_path = f"{mode}/current/{coin}/HODL.json"
        state = load_firebase_json(state_path, user_id, token)

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

        # === Execute trade ===
        execute_trade(
            user_id=user_id,
            bot_name="rebalance_hodl",
            action=side,
            amount=coin_amount,
            price=current_price,
            mode=mode,
            coin=coin
        )

        # === Update snapshot balances
        if side == "buy":
            new_balance = current_balance + coin_amount
            usd_balance -= trade_usd
        else:
            new_balance = max(0, current_balance - coin_amount)
            usd_balance += trade_usd

        current_snapshot["coins"][coin] = {
            "balance": round(new_balance, 8),
            "price": current_price,
            "value": round(new_balance * current_price, 2)
        }

        updated_coins[coin] = new_balance

        # === Update HODL state
        state.update({
            "status": "Holding",
            "amount": round(new_balance, 8),
            "buy_price": current_price,
            "timestamp": datetime.utcnow().isoformat()
        })
        save_firebase_json(state_path, state, user_id, token)

    # === Final snapshot update
    current_snapshot["usd_balance"] = round(usd_balance, 2)
    current_snapshot["timestamp"] = datetime.utcnow().isoformat()
    current_snapshot["total_value"] = round(
        usd_balance + sum(c["balance"] * c["price"] for c in current_snapshot["coins"].values()), 2
    )
    save_firebase_json(snapshot_path, current_snapshot, user_id, token)

    print("✅ Rebalancing complete.")
