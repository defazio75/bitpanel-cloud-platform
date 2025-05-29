# /dashboard/utils/state_loader.py

import os
import json
import csv
from config.config import get_mode
from utils.json_utils import load_user_state, get_user_data_path


# === Portfolio Summary (Aggregates all bot states per coin) ===
def load_portfolio_summary(user_id, mode=None):
    if not mode:
        mode = get_mode(user_id)

    state_folder = os.path.join("data", f"json_{mode}", user_id, "current")
    portfolio_summary = {}

    if not os.path.exists(state_folder):
        return portfolio_summary

    for coin_folder in os.listdir(state_folder):
        coin_path = os.path.join(state_folder, coin_folder)
        if not os.path.isdir(coin_path):
            continue

        for filename in os.listdir(coin_path):
            if filename.endswith(".json"):
                bot_name = filename.replace(".json", "")
                full_path = os.path.join(coin_path, filename)

                with open(full_path, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}

                portfolio_summary[bot_name] = {
                    'btc_held': data.get('btc_held', 0.0),
                    'usd_value': data.get('usd_value', 0.0),
                    'status': data.get('status', 'Unknown')
                }

    return portfolio_summary


# === Load Trade Log (CSV) ===
def load_trade_log(user_id, mode=None):
    if not mode:
        mode = get_mode(user_id)

    log_path = os.path.join("data", f"json_{mode}", user_id, "logs", "trade_log.csv")

    if not os.path.exists(log_path):
        return []

    try:
        with open(log_path, 'r') as f:
            reader = csv.DictReader(f)
            return [row for row in reader if any(row.values())]
    except Exception as e:
        print(f"⚠️ Error loading trade log: {e}")
        return []


# === Load All Bot States ===
def load_bot_states(user_id, mode=None):
    if not mode:
        mode = get_mode(user_id)

    bot_states = {}
    state_folder = os.path.join("data", f"json_{mode}", user_id, "current")

    if not os.path.exists(state_folder):
        return bot_states

    for coin_folder in os.listdir(state_folder):
        coin_path = os.path.join(state_folder, coin_folder)
        if not os.path.isdir(coin_path):
            continue

        for filename in os.listdir(coin_path):
            if filename.endswith(".json"):
                bot_name = filename.replace(".json", "")
                full_path = os.path.join(coin_path, filename)

                with open(full_path, 'r') as f:
                    try:
                        state_data = json.load(f)
                    except json.JSONDecodeError:
                        state_data = {}

                bot_states[bot_name] = state_data

    return bot_states


# === Global Allocations Loader (no user scope) ===
def load_allocations():
    path = os.path.join('config', 'allocations.json')
    with open(path, 'r') as f:
        return json.load(f)
