import os
import json
import csv
import time
from utils.market_data_handler import get_price_data
from utils.performance_tracker import snapshot_portfolio

def reset_paper_account():
    print("🔄 Resetting paper trading environment...")

    coins = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]
    
    os.makedirs("data/json_paper/portfolio", exist_ok=True)
    portfolio_path = "data/json_paper/portfolio/portfolio_snapshot.json"
    portfolio_data = {
        "total_value": 100000.0,
        "usd_balance": 100000.0,
        "coins": {coin: {"balance": 0.0} for coin in coins}
    }
    with open(portfolio_path, "w") as f:
        json.dump(portfolio_data, f, indent=4)
    print("💰 Reset portfolio snapshot to $100,000 USD and 0 coins.")

    os.makedirs("data/logs/paper", exist_ok=True)
    log_path = "data/logs/paper/portfolio_log.csv"
    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "bot_name", "coin", "action", "price", "amount", "mode"])
    print("📄 Cleared trade log.")

    # ✅ Reset unified strategy state files
    current_path = "data/json_paper/current"
    os.makedirs(current_path, exist_ok=True)
    reset_state = {
        "HODL": {"status": "Inactive", "amount": 0.0, "buy_price": 0.0},
        "RSI 5-Min": {"status": "Inactive"},
        "RSI 1-Hour": {"status": "Inactive"},
        "Bollinger Bot": {"status": "Inactive"}
    }
    for coin in coins:
        file_path = os.path.join(current_path, f"{coin}_state.json")
        with open(file_path, "w") as f:
            json.dump(reset_state, f, indent=2)
    print("🧠 Reset all unified bot state files.")

    # ✅ Reset performance logs per coin
    perf_folder = "data/json_paper/performance"
    os.makedirs(perf_folder, exist_ok=True)
    for coin in coins:
        with open(os.path.join(perf_folder, f"{coin.lower()}_profits.json"), "w") as f:
            json.dump({"history": []}, f, indent=2)
    print("📉 Reset performance files.")

    # ✅ Reset historical portfolio snapshots
    history_path = "data/json_paper/portfolio/history"
    if os.path.exists(history_path):
        for file in os.listdir(history_path):
            if file.endswith(".json"):
                os.remove(os.path.join(history_path, file))
        print("🗑️ Cleared historical performance snapshots.")

    # Final snapshot
    time.sleep(0.1)
    price_data = get_price_data()
    snapshot_portfolio(price_data, mode="paper")
    print("📸 Snapshot file updated.")
    print("✅ Paper account reset complete.")
