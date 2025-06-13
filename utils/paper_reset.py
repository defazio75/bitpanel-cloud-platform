import os
import csv
import json
import time
from datetime import datetime

from utils.firebase_db import (
    save_portfolio_snapshot,
    save_coin_state,
    save_performance_snapshot
)
from utils.firebase_config import firebase

def reset_paper_account(user_id):
    if not user_id:
        raise ValueError("❌ user_id is required to reset the paper account.")

    print(f"🔄 Resetting paper account for user: {user_id}...")

    token = st.session_state.user["token"]
    mode = "paper"
    coins = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]

    # === 1. Reset portfolio snapshot ===
    portfolio_dir = os.path.join("data", "json_paper", user_id, "portfolio")
    os.makedirs(portfolio_dir, exist_ok=True)
    portfolio_path = os.path.join(portfolio_dir, "portfolio_snapshot.json")
    portfolio_data = {
        "total_value": 100000.0,
        "usd_balance": 100000.0,
        "holdings": {},
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    with open(portfolio_path, "w") as f:
        json.dump(portfolio_data, f, indent=4)

    save_portfolio_snapshot(user_id, portfolio_data, token, mode)
    print("💰 Reset portfolio snapshot and balances to $100,000 USD and 0 coins.")

    # === 2. Reset trade log ===
    log_dir = os.path.join("data", "logs", "paper", user_id)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "portfolio_log.csv")
    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "bot_name", "coin", "action", "price", "amount", "mode"])
    print("📄 Cleared trade log.")

    # === 3. Reset unified strategy state files ===
    current_path = os.path.join("data", "json_paper", user_id, "current")
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
        save_coin_state(user_id, coin, reset_state, token, mode)
    print("🧠 Reset all unified bot state files and saved to Firebase.")

    # === 4. Reset performance logs per coin ===
    perf_folder = os.path.join("data", "json_paper", user_id, "performance")
    os.makedirs(perf_folder, exist_ok=True)
    for coin in coins:
        perf_path = os.path.join(perf_folder, f"{coin.lower()}_profits.json")
        with open(perf_path, "w") as f:
            json.dump({"history": []}, f, indent=2)
        save_performance_snapshot(user_id, {"history": []}, "init", token, mode)
    print("📉 Reset performance files and synced with Firebase.")

    # === 5. Clear historical snapshots ===
    history_path = os.path.join(portfolio_dir, "history")
    if os.path.exists(history_path):
        for file in os.listdir(history_path):
            if file.endswith(".json"):
                os.remove(os.path.join(history_path, file))
    db = firebase.database()
    db.child("users").child(user_id).child(mode).child("history").remove(token)
    print("🗑️ Cleared historical performance snapshots in Firebase and locally.")

    print(f"✅ Paper account reset complete for user: {user_id}")
