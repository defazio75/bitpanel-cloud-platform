import os
import json

def get_account_summary(user_id, mode="paper"):
    snapshot_path = os.path.join("data", f"json_{mode}", user_id, "portfolio", "portfolio_snapshot.json")

    try:
        with open(snapshot_path, "r") as f:
            snapshot = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ No snapshot found for {user_id} in {mode} mode.")
        return {
            "usd_balance": 0.0,
            "coins": {},
            "total_value": 0.0
        }

    summary = {
        "usd_balance": round(snapshot.get("usd_balance", 0.0), 2),
        "total_value": round(snapshot.get("total_value", 0.0), 2),
        "coins": {}
    }

    for coin, data in snapshot.get("coins", {}).items():
        summary["coins"][coin] = {
            "balance": round(data.get("balance", 0.0), 8),
            "price": round(data.get("price", 0.0), 2),
            "value": round(data.get("value", 0.0), 2)
        }

    return summary
