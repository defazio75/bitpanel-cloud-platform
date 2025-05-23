import os
import json

def load_total_profit(mode="paper"):
    """
    Load and sum total_profit_usd across all performance files by coin
    """
    path = os.path.join("data", f"json_{mode}", "performance")
    if not os.path.exists(path):
        return 0.0

    total_profit = 0.0
    for filename in os.listdir(path):
        if filename.endswith("_profits.json"):
            file_path = os.path.join(path, filename)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    total_profit += data.get("total_profit_usd", 0.0)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    return round(total_profit, 2)