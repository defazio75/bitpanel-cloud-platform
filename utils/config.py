# config/config.py

import json
import os
import streamlit as st

# === Default Strategy Configuration ===

# Allocation settings
BTC_HOLDING_PERCENT = 0.25
RSI_5MIN_ALLOC_PERCENT = 0.25
RSI_1HR_ALLOC_PERCENT = 0.25
BOLLINGER_ALLOC_PERCENT = 0.25

# RSI Strategy
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_5MIN_PROFIT_TARGET = 0.02
RSI_1HR_PROFIT_TARGET = 0.03

# Bollinger Band Strategy
BOLLINGER_WINDOW = 20
BOLLINGER_DEV = 2
BOLLINGER_PROFIT_TRIGGER = 0.02
BOLLINGER_TRAIL_DROP = 0.01

# Market settings
BASE_PAIR = 'XXBTZUSD'
QUOTE_ASSET = 'ZUSD'

# General
MIN_TRADE_USD = 10

# === Multi-User Mode Handling ===

def get_user_mode_path(user_id):
    return os.path.join("config", "user_modes", f"{user_id}.json")

def save_mode(mode, user_id):
    try:
        os.makedirs("config/user_modes", exist_ok=True)
        with open(get_user_mode_path(user_id), "w") as f:
            json.dump({"mode": mode}, f)
        st.session_state["mode"] = mode
    except Exception as e:
        print(f"❌ Failed to save mode for user {user_id}: {e}")

def get_mode(user_id):
    if "mode" in st.session_state:
        return st.session_state["mode"]

    path = get_user_mode_path(user_id)

    try:
        with open(path, "r") as f:
            mode = json.load(f).get("mode", "paper")
    except (FileNotFoundError, json.JSONDecodeError):
        mode = "paper"

    st.session_state["mode"] = mode
    return mode
