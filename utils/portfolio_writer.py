import os
import pandas as pd
import pytz
from datetime import datetime
from utils.config import get_mode
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.firebase_db import (
    save_portfolio_snapshot,
    load_portfolio_snapshot,
    save_coin_state,
    load_coin_state,
)

print("📦 portfolio_writer module loaded")

def write_portfolio_snapshot(user_id, mode="paper", token=None):
    print(f"[WRITER] Running portfolio_writer for {user_id} in {mode} mode")

    snapshot = load_portfolio_snapshot(user_id, token, mode)
    if not snapshot:
        print(f"❌ No existing snapshot found for {user_id} in {mode} mode. Skipping.")
        return

    prices = get_prices(user_id=user_id)
    total_usd = 0.0

    for coin, data in snapshot.get("coins", {}).items():
        balance = float(data.get("balance", 0.0))
        price = prices.get(coin.upper(), 0.0)
        value = round(balance * price, 2)

        snapshot["coins"][coin]["price"] = round(price, 2)
        snapshot["coins"][coin]["value"] = value
        total_usd += value

    usd_balance = float(snapshot.get("usd_balance", 0.0))
    snapshot["total_usd"] = round(total_usd + usd_balance, 2)
    snapshot["timestamp"] = datetime.utcnow().isoformat()

    # === Save to Firebase main snapshot ===
    save_portfolio_snapshot(user_id, snapshot, token, mode)
    print(f"✅ Portfolio snapshot updated for {user_id} — Total USD: ${snapshot['total_usd']:.2f}")

    # === Check if it's 7:00 PM CST to save history snapshot ===
    now_cst = datetime.now(pytz.timezone("US/Central"))
    if now_cst.hour == 19 and now_cst.minute == 0:
        save_portfolio_history_snapshot(user_id, snapshot, token, mode)
        print("🕖 Daily portfolio snapshot saved to history.")
