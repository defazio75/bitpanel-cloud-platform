import streamlit as st
from utils.kraken_wrapper import get_prices
from utils.firebase_db import load_portfolio_snapshot
import pandas as pd
import os
from datetime import datetime

def render_current_positions(mode, user_id, token):
    st.title("📍 Current Positions")

    # === Load Prices and Portfolio ===
    prices = get_prices(user_id=user_id)
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    total_value = snapshot.get("total_value", 0.0)
    usd_balance = snapshot.get("usd_balance", 0.0)
    coin_data = snapshot.get("coins", {})

    # === Count Active Strategies ===
    from utils.firebase_db import load_coin_state
    strategy_count = 0
    for coin in coin_data:
        state = load_coin_state(user_id=user_id, coin=coin, token=token, mode=mode)
        for strat in state:
            if state[strat].get("status") == "Active":
                strategy_count += 1

    # === Load Recent Trade Log ===
    trade_log_path = f"data/logs/trade_log_{mode}.csv"
    last_trade = "—"
    if os.path.exists(trade_log_path):
        df = pd.read_csv(trade_log_path)
        if not df.empty:
            last_row = df.sort_values("timestamp", ascending=False).iloc[0]
            ts = pd.to_datetime(last_row["timestamp"]).strftime("%I:%M %p")
            last_trade = f'{last_row["coin"]} - {last_row["strategy"]} - {last_row["action"].upper()} @ {last_row["price"]:.2f} ({ts})'

    # === Layout ===
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💼 Total Portfolio", f"${total_value:,.2f}")
    col2.metric("💰 USD Balance", f"${usd_balance:,.2f}")
    col3.metric("🤖 Bots Active", f"{strategy_count} strategies")
    col4.metric("⏱️ Last Trigger", last_trade)
