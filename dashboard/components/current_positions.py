import streamlit as st
from utils.kraken_wrapper import get_prices
from utils.firebase_db import load_portfolio_snapshot
import pandas as pd
import os
from datetime import datetime

def calculate_live_portfolio_value(snapshot, prices):
    total = snapshot.get("usd_balance", 0.0)

    for coin, data in snapshot.get("coins", {}).items():
        balance = data.get("balance", 0.0)
        price = prices.get(coin, 0.0)  # This is already a float
        total += round(balance * price, 2)

    return round(total, 2)

def render_current_positions(mode, user_id, token):
    st.title("📍 Current Positions")
    st.subheader("🧠 Overview Pulse")
    st.caption("A real-time snapshot of your portfolio and active strategy activity.")

    # === Load Prices and Portfolio ===
    prices = get_prices(user_id=user_id)
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    total_value = calculate_live_portfolio_value(snapshot, prices)
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

    # === Per-Coin Strategy Cards ===
    st.markdown("---")
    st.subheader("📦 Current Strategy Details")

    # We’ll start with BTC
    coin = "BTC"
    coin_upper = coin.upper()
    coin_price = prices.get(coin_upper, 0.0)
    coin_state = load_coin_state(user_id=user_id, coin=coin_upper, token=token, mode=mode)

    # Get strategy names
    strategies = ["HODL", "RSI_5MIN", "RSI_1HR", "BOLLINGER"]

    total_coin = 0.0
    total_usd = 0.0
    active_count = 0
    table_rows = []

    for strat in strategies:
        s = coin_state.get(strat, {})
        amount = s.get("amount", 0.0)
        usd_held = s.get("usd_held", 0.0)
        status = s.get("status", "Inactive")
        buy_price = s.get("buy_price", 0.0)
        indicator = s.get("indicator", "—")
        target = s.get("target", "—")
        last_action = s.get("last_action", "—")

        total = round((amount * coin_price) + usd_held, 2)
        initial_value = (amount * buy_price if buy_price else 0) + usd_held
        pnl = round(total - initial_value, 2) if status == "Active" else 0.0

        if status == "Active":
            active_count += 1

        table_rows.append({
            "Strategy": strat,
            "Status": status,
            "Amount": f"{amount:.6f}",
            "USD Value": f"${total:,.2f}",
            "Indicator": indicator,
            "Target": target,
            "P/L": f"${pnl:,.2f}",
            "Last Action": last_action
        })

        total_coin += amount
        total_usd += total

    df = pd.DataFrame(table_rows)
    df.index = [""] * len(df)  # This hides the row index
    with st.expander(f"💰 {coin_upper} — ${total_usd:,.2f} | {total_coin:.6f} {coin_upper} | {active_count} Bots Active", expanded=False):
        st.table(df)
