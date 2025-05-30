import os
import json
from datetime import datetime
from utils.kraken_wrapper import get_prices
from utils.config import get_mode
from trade_executor import execute_trade

def rebalance_hodl(user_id):
    mode = get_mode(user_id=user_id)
    print(f"[Rebalance HODL] Running in {mode.upper()} mode...")

    folder = f"json_{mode}/{user_id}"
    snapshot_path = os.path.join("data", folder, "portfolio", "portfolio_snapshot.json")
    state_dir = os.path.join("data", folder, "current")

    if not os.path.exists(snapshot_path):
        print("❌ portfolio_snapshot.json not found.")
        return

    with open(snapshot_path, "r") as f:
        current_snapshot = json.load(f)

    prices = get_prices(user_id=user_id)
    usd_balance = current_snapshot.get("usd_balance", 0)
    updated_coins = {}

    for filename in os.listdir(state_dir):
        if not filename.endswith("_state.json"):
            continue

        coin = filename.replace("_state.json", "")
        state_path = os.path.join(state_dir, filename)

        with open(state_path, "r") as f:
            state = json.load(f)

        if "HODL" not in state or "target_usd" not in state["HODL"]:
            continue  # skip coins without HODL targets

        target_usd = state["HODL"]["target_usd"]
        current_price = prices.get(coin, 0)
        current_coin_data = current_snapshot.get("coins", {}).get(coin, {"balance": 0})
        current_balance = current_coin_data.get("balance", 0)
        current_value = current_balance * current_price

        delta = round(target_usd - current_value, 2)
        if abs(delta) < 1 or current_price == 0:
            continue  # skip small or invalid trades

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

        # === Update simulated portfolio snapshot
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

        # === Update HODL bot state
        state["HODL"].update({
            "status": "Holding",
            "amount": round(new_balance, 8),
            "buy_price": current_price,
            "timestamp": datetime.utcnow().isoformat()
        })

        with open(state_path, "w") as f:
            json.dump(state, f, indent=2)

    # Save updated snapshot
    current_snapshot["usd_balance"] = round(usd_balance, 2)
    current_snapshot["timestamp"] = datetime.utcnow().isoformat()
    current_snapshot["total_value"] = round(
        usd_balance + sum(coin["balance"] * coin["price"] for coin in current_snapshot["coins"].values()), 2
    )

    with open(snapshot_path, "w") as f:
        json.dump(current_snapshot, f, indent=2)

    print("✅ Rebalancing complete.")
