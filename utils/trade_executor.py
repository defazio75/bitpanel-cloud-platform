from datetime import datetime
from utils.config import get_mode
from utils.kraken_wrapper import rate_limited_query_private
from utils.performance_logger import log_execution_event
from utils.firebase_db import (
    load_firebase_json,
    save_firebase_json,
    load_firebase_csv,
    save_firebase_csv
)
import streamlit as st
import pandas as pd

# === Main Execution Function ===
def execute_trade(bot_name, action, amount, price, mode=None, coin="BTC", user_id=None):
    if not mode:
        mode = get_mode()
    if not user_id:
        raise ValueError("❌ user_id is required for execute_trade.")

    token = st.session_state.user["token"]

    # Log internal audit
    log_execution_event(
        bot_name=bot_name,
        action=action,
        coin=coin,
        amount=amount,
        price=price,
        mode=mode,
        user_id=user_id,
        message="Executed via execute_trade()"
    )

    order = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "bot_name": bot_name,
        "coin": coin,
        "action": action,
        "price": round(price, 2),
        "amount": round(amount, 6),
        "mode": mode,
        "user_id": user_id
    }

    print(f"📝 [{bot_name.upper()}] {action.upper()} {order['amount']} {coin} @ ${order['price']:,.2f}")

    if mode == "paper":
        log_trade(order, mode, user_id, token)
    else:
        send_live_order(order, token)

# === Paper Trade Logger ===
def log_trade(order, mode, user_id, token):
    log_trade_to_csv(order, mode, user_id, token)
    update_portfolio_snapshot(order, mode, user_id, token)

def log_trade_to_csv(order, mode, user_id, token):
    path = f"{mode}/trades/trade_log.csv"
    try:
        df_existing = load_firebase_csv(path, user_id, token)
    except:
        df_existing = pd.DataFrame()

    new_row = pd.DataFrame([order])
    df_updated = pd.concat([df_existing, new_row], ignore_index=True)
    save_firebase_csv(path, df_updated, user_id, token)

# === Portfolio Snapshot Updater ===
def update_portfolio_snapshot(order, mode, user_id, token):
    snapshot_path = f"{mode}/balances/portfolio_snapshot.json"
    portfolio = load_firebase_json(snapshot_path, user_id, token) or {
        "usd_balance": 0.0,
        "coins": {},
        "timestamp": None,
        "total_value": 0.0
    }

    coin = order['coin']
    action = order['action']
    amount = float(order['amount'])
    price = float(order['price'])
    usd_change = amount * price

    portfolio.setdefault("coins", {})
    coin_data = portfolio["coins"].get(coin, {"balance": 0.0, "price": price, "value": 0.0})
    current_balance = coin_data.get("balance", 0.0)

    if action == "buy":
        if portfolio.get("usd_balance", 0) >= usd_change:
            portfolio["usd_balance"] -= usd_change
            current_balance += amount
    elif action == "sell":
        if current_balance >= amount:
            portfolio["usd_balance"] += usd_change
            current_balance -= amount

    portfolio["coins"][coin] = {
        "balance": round(current_balance, 8),
        "price": price,
        "value": round(current_balance * price, 2)
    }

    portfolio["timestamp"] = datetime.utcnow().isoformat()
    portfolio["total_value"] = round(
        portfolio["usd_balance"] +
        sum(coin["balance"] * coin["price"] for coin in portfolio["coins"].values()),
        2
    )

    save_firebase_json(snapshot_path, portfolio, user_id, token)

# === Live Trade Execution (Kraken API) ===
def send_live_order(order, token):
    print("🚀 Sending live order to exchange:")
    print(order)

    try:
        coin = order["coin"]
        side = order["action"]
        volume = order["amount"]
        pair_map = {
            "BTC": "XXBTZUSD", "ETH": "XETHZUSD", "SOL": "SOLUSD",
            "XRP": "XXRPZUSD", "DOT": "DOTUSD", "LINK": "LINKUSD"
        }

        kraken_pair = pair_map.get(coin)
        if not kraken_pair:
            print(f"❌ Unsupported coin: {coin}")
            return

        params = {
            "pair": kraken_pair,
            "type": side,
            "ordertype": "market",
            "volume": round(volume, 6)
        }

        result = rate_limited_query_private("AddOrder", params)
        print("✅ Kraken order response:", result)

        if result.get("error"):
            print("❌ Kraken returned error:", result["error"])
            return

        # Log to live portfolio
        user_id = order["user_id"]
        log_trade(order, "live", user_id, token)

    except Exception as e:
        print(f"❌ Error placing Kraken order: {e}")
