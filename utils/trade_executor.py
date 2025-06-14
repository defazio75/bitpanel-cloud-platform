from datetime import datetime
from utils.config import get_mode
from exchange.exchange_manager import get_exchange
from utils.kraken_wrapper import rate_limited_query_private
from utils.load_keys import load_user_api_keys
from utils.logger import log_trade_multi
from utils.firebase_db import (
    load_portfolio_snapshot,
    save_portfolio_snapshot,
    load_coin_state,
    save_coin_state
)
import pandas as pd

def get_exchange_for_user(user_id, token=None):
    mode = get_mode(user_id)
    api_keys = load_user_api_keys(user_id, token)
    user_exchange = api_keys.get("exchange", "kraken")
    return get_exchange(user_exchange, mode=mode, api_keys=api_keys)

# === Main Execution Function ===
def execute_trade(bot_name, action, amount, price, mode=None, coin="BTC", user_id=None):
    if not mode:
        mode = get_mode()
    if not user_id:
        raise ValueError("❌ user_id is required for execute_trade.")

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
    send_live_order(order, token)

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
        user_id = order["user_id"]
        coin = order["coin"]
        bot_name = order.get("bot_name", "Unknown")
        action = order["action"]
        amount = order["amount"]
        price = order["price"]
        mode = order["mode"]
        
        side = action
        volume = amount
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

        exchange = get_exchange_for_user(user_id, token)
        result = exchange.place_market_order(coin=coin, volume=volume, side=side)
        print("✅ Kraken order response:", result)

        if result.get("error"):
            print("❌ Kraken returned error:", result["error"])
            return

        txids = result.get("result", {}).get("txid")
        if not txids:
            print("❌ Trade failed — no txid returned.")
            return

        print(f"✅ Trade successful — Kraken TXID: {txids}")

        # Log to live portfolio
        log_trade_multi(
            user_id=user_id,
            coin=coin,
            strategy="Manual Trade",
            action=action,
            amount=amount,
            price=price,
            mode=mode,
            notes="Executed via live Kraken order"
        )

    except Exception as e:
        print(f"❌ Error placing Kraken order: {e}")
