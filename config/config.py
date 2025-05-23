# === Strategy Configuration ===

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

# === Mode Handling ===

import json
import os
import streamlit as st  # ✅ Needed for session state access

CONFIG_FILE = "config/user_settings.json"

def save_mode(mode):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"mode": mode}, f)
        st.session_state["mode"] = mode
    except Exception as e:
        print(f"Failed to save mode: {e}")

def get_mode():
    if "mode" in st.session_state:
        return st.session_state["mode"]
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f).get("mode", "paper")
    except (FileNotFoundError, json.JSONDecodeError):
        return "paper"
