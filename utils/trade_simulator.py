import os
import json
from datetime import datetime
from utils.firebase_db import save_firebase_json, append_firebase_csv
from utils.state_loader import load_strategy_state
from utils.portfolio_loader import load_portfolio_snapshot
from utils.config import get_mode
from utils.kraken_wrapper import get_prices


def simulate_trade(user_id, coin, action, amount, price=None):
    mode = get_mode(user_id)

    # === Load current snapshot ===
    snapshot = load_portfolio_snapshot(user_id, mode)
    prices = get_prices(user_id=user_id)
    price = price or prices.get(coin.upper(), 0)
    usd_value = amount * price

    # === Adjust balances ===
    if action == "buy":
        if snapshot.get("usd_balance", 0) < usd_value:
            print(f"❌ Not enough USD to simulate buy of {amount} {coin.upper()}.")
            return
        snapshot[coin] = snapshot.get(coin, 0) + amount
        snapshot["usd_balance"] -= usd_value

    elif action == "sell":
        if snapshot.get(coin, 0) < amount:
            print(f"❌ Not enough {coin.upper()} to simulate sell of {amount}.")
            return
        snapshot[coin] -= amount
        snapshot["usd_balance"] += usd_value

    else:
        print("❌ Invalid action. Must be 'buy' or 'sell'.")
        return

    # === Save updated snapshot ===
    snapshot_path = f"portfolio/portfolio_snapshot.json"
    save_firebase_json(user_id, snapshot_path, snapshot, mode)

    # === Log trade ===
    trade_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "coin": coin.upper(),
        "action": action,
        "amount": round(amount, 8),
        "price": round(price, 2),
        "value_usd": round(usd_value, 2)
    }
    append_firebase_csv(user_id, "trade_log.csv", trade_entry, mode)

    print(f"✅ Simulated {action} of {amount} {coin.upper()} at ${price:.2f}.")

    # === Optional: Update strategy state ===
    state = load_strategy_state(coin.upper(), mode, user_id)
    strategy_key = f"HODL" if "HODL" in state else next(iter(state.keys()), None)
    if strategy_key:
        strategy_block = state.get(strategy_key, {})
        strategy_block["amount"] = strategy_block.get("amount", 0) + amount if action == "buy" else strategy_block.get("amount", 0) - amount
        strategy_block["usd_held"] = strategy_block.get("usd_held", 0)
        state[strategy_key] = strategy_block
        save_firebase_json(user_id, f"current/{coin.upper()}_state.json", state, mode)

        print(f"📦 Updated {coin.upper()} strategy state for {strategy_key}.")
