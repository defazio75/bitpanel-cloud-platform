import os
import json

def load_portfolio_snapshot(user_id, mode="paper"):
    """
    Loads the portfolio snapshot for a specific user and mode.

    Args:
        user_id (str): Unique user identifier
        mode (str): 'paper' or 'live'

    Returns:
        dict: Portfolio snapshot with total value, USD balance, and coin breakdown
    """
    path = os.path.join("data", f"json_{mode}", user_id, "portfolio", "portfolio_snapshot.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Portfolio snapshot not found for user {user_id} in mode: {mode}")
        return {
            "total_value": 0.0,
            "usd_balance": 0.0,
            "coins": {}
        }
