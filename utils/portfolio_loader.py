import os
import json

def load_portfolio_snapshot(mode="paper"):
    path = os.path.join("data", f"json_{mode}", "portfolio", "portfolio_snapshot.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Portfolio snapshot not found for mode: {mode}")
        return {
            "total_value": 0.0,
            "usd_balance": 0.0,
            "coins": {}
        }