import os
import json
from datetime import datetime
from utils.firebase_db import load_firebase_json, save_firebase_json
from utils.config import get_mode

# === Load or Initialize Profit Summary ===
def load_profit_summary(user_id, coin, mode=None):
    if not mode:
        mode = get_mode(user_id)

    path = f"users/{user_id}/{mode}/performance/{coin}_profits.json"
    summary = load_firebase_json(path, user_id)
    if not summary:
        summary = {
            "daily": 0.0,
            "weekly": 0.0,
            "monthly": 0.0,
            "yearly": 0.0,
            "total": 0.0,
            "last_updated": datetime.utcnow().isoformat()
        }
    return summary

# === Save Updated Profit Summary ===
def save_profit_summary(user_id, coin, data, mode=None):
    if not mode:
        mode = get_mode(user_id)

    path = f"users/{user_id}/{mode}/performance/{coin}_profits.json"
    data["last_updated"] = datetime.utcnow().isoformat()
    save_firebase_json(path, data, user_id)

# === Update Profit Summary with New Gain/Loss ===
def update_profit_summary(user_id, coin, profit_change, mode=None):
    summary = load_profit_summary(user_id, coin, mode)
    summary["daily"] += profit_change
    summary["weekly"] += profit_change
    summary["monthly"] += profit_change
    summary["yearly"] += profit_change
    summary["total"] += profit_change
    save_profit_summary(user_id, coin, summary, mode)

