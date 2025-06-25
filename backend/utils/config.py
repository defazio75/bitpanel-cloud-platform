import json
import os

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

def get_mode(user_id=None):
    try:
        import streamlit as st
        return st.session_state.get("mode", "paper")
    except:
        # Fall back to reading from Firebase or default to "paper"
        # If you have user-specific mode stored, use that here:
        return "paper"  # or load from firebase if needed

def set_mode(mode):
    st.session_state["mode"] = mode
