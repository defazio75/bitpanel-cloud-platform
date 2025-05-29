import os
import json
import csv
from datetime import datetime

def snapshot_portfolio(price_data, user_id, mode="paper"):
    """
    Saves a snapshot of the current portfolio for a given user.
    
    Args:
        price_data (dict): Dictionary of coin prices (e.g., {"BTC": 40000, ...})
        user_id (str): Unique identifier for the user
        mode (str): "paper" or "live"
    """
    if not user_id:
        raise ValueError("❌ user_id is required to snapshot portfolio.")

    base_path = os.path.join("data", f"json_{mode}", user_id)
    snapshot_json_path = os.path.join(base_path, "portfolio", "portfolio_snapshot.json")
    log_csv_path = os.path.join("data", "logs", mode, user_id, "portfolio_log.csv")

    timestamp = datetime.utcnow().isoformat() + "Z"

    # Load existing snapshot or use defaults
    try:
        with open(snapshot_json_path, "r") as f:
            existing_snapshot = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ No existing snapshot found for {user_id}. Using defaults.")
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
        "total_value": round(usd_balance, 2)
    }

    # Compute coin values
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

    # Save JSON snapshot
    os.makedirs(os.path.dirname(snapshot_json_path), exist_ok=True)
    with open(snapshot_json_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    # Save CSV log
    os.makedirs(os.path.dirname(log_csv_path), exist_ok=True)
    with open(log_csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, mode, snapshot["total_value"]])

    print(f"📸 Snapshot saved for {user_id} in {mode} mode: ${snapshot['total_value']:.2f}")
