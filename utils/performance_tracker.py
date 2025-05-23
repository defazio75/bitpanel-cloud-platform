
import os
import json
import csv
from datetime import datetime

def snapshot_portfolio(price_data, mode="paper"):
    base_path = os.path.join("data", f"json_{mode}")
    snapshot_json_path = os.path.join(base_path, "portfolio", "portfolio_snapshot.json")
    log_csv_path = os.path.join("data", "logs", mode, "portfolio_log.csv")

    timestamp = datetime.utcnow().isoformat() + "Z"

    try:
        with open(snapshot_json_path, "r") as f:
            existing_snapshot = json.load(f)
    except FileNotFoundError:
        print("⚠️ No existing snapshot found. Using defaults.")
        existing_snapshot = {
            "usd_balance": 100000.0,
            "coins": {
                "BTC": {"balance": 0.0},
                "ETH": {"balance": 0.0},
                "XRP": {"balance": 0.0},
                "DOT": {"balance": 0.0},
                "LINK": {"balance": 0.0},
                "SOL": {"balance": 0.0}
            }
        }

    usd_balance = existing_snapshot.get("usd_balance", 0.0)
    coins = existing_snapshot.get("coins", {})

    snapshot = {
        "timestamp": timestamp,
        "mode": mode,
        "usd_balance": usd_balance,
        "coins": {},
        "total_value": 0.0
    }

    snapshot["total_value"] += usd_balance

    for coin, data in coins.items():
        balance = data.get("balance", 0.0)
        price = price_data.get(coin, 0.0)
        value = round(balance * price, 2)
        snapshot["coins"][coin] = {
            "balance": balance,
            "price": price,
            "value": value
        }
        snapshot["total_value"] += value

    os.makedirs(os.path.dirname(snapshot_json_path), exist_ok=True)
    with open(snapshot_json_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    os.makedirs(os.path.dirname(log_csv_path), exist_ok=True)
    with open(log_csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, mode, snapshot["total_value"]])
