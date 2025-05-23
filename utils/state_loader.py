# /dashboard/utils/state_loader.py
from config.config import get_mode
import os
import json
import csv

def load_portfolio_summary(mode=None):
    if not mode:
        mode = get_mode()

    state_folder = os.path.join("data", f"json_{mode}", "current")
    portfolio_summary = {}

    if not os.path.exists(state_folder):
        return portfolio_summary

    for coin_folder in os.listdir(state_folder):
        coin_path = os.path.join(state_folder, coin_folder)
        if not os.path.isdir(coin_path):
            continue  # skip non-folders

        for filename in os.listdir(coin_path):
            if filename.endswith(".json"):
                bot_name = filename.replace(".json", "")
                full_path = os.path.join(coin_path, filename)
                with open(full_path, 'r') as f:
                    data = json.load(f)
                    portfolio_summary[bot_name] = {
                        'btc_held': data.get('btc_held', 0.0),
                        'usd_value': data.get('usd_value', 0.0),
                        'status': data.get('status', 'Unknown')
                    }

    return portfolio_summary

def load_balances(mode=None):
    if not mode:
        mode = get_mode()

    balances = {}
    folder_path = os.path.join("data", f"json_{mode}", "balances")

    if not os.path.exists(folder_path):
        return balances

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            coin = filename.replace(".json", "").upper()
            try:
                with open(os.path.join(folder_path, filename), "r") as f:
                    data = json.load(f)
                    balance = data.get("balance", 0.0)
                    balances[coin] = balance
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    return balances

def load_trade_log(mode=None, coin_filter=None):
    if not mode:
        mode = get_mode()

    log_path = os.path.join("data", f"json_{mode}", "logs", "trade_log.csv")

    if not os.path.exists(log_path):
        return []

    try:
        with open(log_path, 'r') as f:
            reader = csv.DictReader(f)
            return [row for row in reader if any(row.values())]  # skip empty rows
    except Exception as e:
        print(f"⚠️ Error loading trade log: {e}")
        return []

def load_allocations():
    path = os.path.join('config', 'allocations.json')
    with open(path, 'r') as f:
        return json.load(f)

def load_bot_states(mode=None):
    if not mode:
        mode = get_mode()

    state_folder = os.path.join("data", f"json_{mode}", "current")
    bot_states = {}

    if not os.path.exists(state_folder):
        return bot_states

    for coin_folder in os.listdir(state_folder):
        coin_path = os.path.join(state_folder, coin_folder)
        if not os.path.isdir(coin_path):
            continue  # skip anything not a folder

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

def save_state(bot_name, state_data, mode=None, coin="BTC"):
    if not mode:
        mode = get_mode()

    coin = coin.upper()
    state_folder = os.path.join("data", f"json_{mode}", "current", coin)
    os.makedirs(state_folder, exist_ok=True)

    state_path = os.path.join(state_folder, f"{bot_name}.json")
    with open(state_path, "w") as f:
        json.dump(state_data, f, indent=4)