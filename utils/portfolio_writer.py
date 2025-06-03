import os
import json
import pandas as pd
from datetime import datetime
from utils.config import get_mode
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.firebase_db import save_firebase_json, load_firebase_json


def write_portfolio_snapshot(user_id, mode=None, token=None):
    if not mode:
        mode = get_mode(user_id)

    prices = get_prices(user_id=user_id)

    # Load balances
    snapshot_path = f"{mode}/balances/portfolio_snapshot.json"
    history_dir = f"{mode}/history"
    log_csv_path = f"{mode}/logs/portfolio_log.csv"

    # Construct snapshot
    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "usd_balance": 0.0,
        "coins": {},
        "total_value": 0.0
    }

    try:
        # Load from previously saved snapshot to grab balances
        # (could also pull live balances if needed)
        portfolio = snapshot.copy()

        for coin, price in prices.items():
            state_path = f"{mode}/current/{coin}_state.json"
            try:
                from utils.firebase_db import load_firebase_json
                state = load_firebase_json(state_path, user_id, token)
            except:
                state = {}

            balance = 0.0
            if "HODL" in state:
                balance += float(state["HODL"].get("amount", 0))
            if "usd_held" in state.get("HODL", {}):
                snapshot["usd_balance"] += float(state["HODL"].get("usd_held", 0))

            for strategy in ["RSI_5MIN", "RSI_1HR", "BOLL"]:
                if strategy in state:
                    balance += float(state[strategy].get("amount", 0))
                    if "usd_held" in state[strategy]:
                        snapshot["usd_balance"] += float(state[strategy].get("usd_held", 0))

            value = balance * price
            snapshot["coins"][coin] = {
                "balance": round(balance, 6),
                "price": price,
                "value": round(value, 2)
            }

            snapshot["total_value"] += value

        snapshot["total_value"] += snapshot["usd_balance"]

        # Save latest snapshot JSON
        save_firebase_json(snapshot_path, snapshot, user_id, token)

        # Save performance log to performance/daily.json
        performance_path = f"{mode}/performance/daily.json"
        performance_data = {
            "timestamp": snapshot["timestamp"],
            "total_value": round(snapshot["total_value"], 2)
        }
        save_firebase_json(performance_path, performance_data, user_id, token)

        # Save history snapshot if between 7:00–7:05 PM CST
        now = datetime.now()
        if now.hour == 19 and now.minute <= 5:
            history_path = f"{history_dir}/{now.strftime('%Y-%m-%d')}.json"
            save_firebase_json(history_path, snapshot, user_id, token)

        # Append to portfolio log CSV
        try:
            df_existing = load_firebase_csv(log_csv_path, user_id, token)
        except:
            df_existing = pd.DataFrame()

        new_row = pd.DataFrame([{
            "timestamp": snapshot["timestamp"],
            "usd_balance": round(snapshot["usd_balance"], 2),
            "total_value": round(snapshot["total_value"], 2)
        }])

        df_updated = pd.concat([df_existing, new_row], ignore_index=True)
        save_firebase_csv(log_csv_path, df_updated, user_id, token)

        print("✅ Portfolio snapshot saved to Firebase.")

    except Exception as e:
        print(f"❌ Error writing portfolio snapshot: {e}")

def save_daily_snapshot(user_id, token, mode):
    balances = get_live_balances(user_id)
    prices = get_prices(user_id)
    
    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "usd_balance": balances.get("USD", 0),
        "coins": {},
        "total_value": 0
    }

    for coin, amount in balances.items():
        if coin == "USD":
            continue
        price = prices.get(coin, 0)
        value = amount * price
        snapshot["coins"][coin] = {
            "balance": round(amount, 6),
            "price": price,
            "value": round(value, 2)
        }
        snapshot["total_value"] += value

    snapshot["total_value"] += snapshot["usd_balance"]

    # Save to Firebase
    path = f"{mode}/balances/portfolio_snapshot"
    save_firebase_json(path, snapshot, user_id, token)

    # Save daily history
    date_path = f"{mode}/history/{datetime.now().strftime('%Y-%m-%d')}.json"
    save_firebase_json(date_path, snapshot, user_id, token)
