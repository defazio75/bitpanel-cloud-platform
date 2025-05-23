import os
import json
import csv
from datetime import datetime

def write_portfolio_snapshot(mode, usd_balance, coin_data):
    now = datetime.now()
    date_str = now.date().isoformat()

    # === 1. Save latest snapshot
    latest_path = os.path.join("data", f"json_{mode}", "portfolio", "portfolio_snapshot.json")
    os.makedirs(os.path.dirname(latest_path), exist_ok=True)

    total_value = usd_balance + sum(c["value"] for c in coin_data.values())

    snapshot = {
        "timestamp": now.isoformat(),
        "date": date_str,
        "mode": mode,
        "usd_balance": usd_balance,
        "coins": coin_data,
        "total_value": total_value
    }

    with open(latest_path, "w") as f:
        json.dump(snapshot, f, indent=2)

    # === 2. If it's 7:00–7:05 PM CST, save historical snapshot
    if now.hour == 19 and now.minute < 5:
        history_path = os.path.join("data", f"json_{mode}", "portfolio", "history", f"{date_str}.json")
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        if not os.path.exists(history_path):
            with open(history_path, "w") as f:
                json.dump(snapshot, f, indent=2)

    # === 3. Log snapshot to CSV (for time-series tracking)
    csv_log_path = os.path.join("data", "logs", mode, "portfolio_log.csv")
    os.makedirs(os.path.dirname(csv_log_path), exist_ok=True)
    with open(csv_log_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([now.isoformat(), mode, total_value])