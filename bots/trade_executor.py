
import json
import os
import csv
from datetime import datetime
from config.config import get_mode
from utils.kraken_wrapper import rate_limited_query_private
from utils.performance_logger import log_execution_event

# === Portfolio Path Helper ===
def get_portfolio_path(user_id, mode):
    return f"data/json_{mode}/{user_id}/portfolio/portfolio_snapshot.json"

# === Main Execution Function ===
def execute_trade(bot_name, action, amount, price, mode=None, coin="BTC", user_id=None):
    if not mode:
        mode = get_mode()

    if not user_id:
        raise ValueError("❌ user_id is required for execute_trade.")

    # Log internal execution audit
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

    portfolio_path = get_portfolio_path(user_id, mode)

    if mode == "paper":
        log_trade(order, mode, portfolio_path, user_id)
    else:
        send_live_order(order)

# === Shared CSV Logger ===
def write_trade_to_csv(order, filepath):
    file_exists = os.path.exists(filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "bot_name", "coin", "action", "price", "amount", "mode", "user_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(order)

# === Paper Trade Logic ===
def log_trade(order, mode, portfolio_path, user_id):
    bot_file = f"{order['bot_name'].split('_')[0]}_trades.csv"
    filepath = os.path.join("data/logs", mode, user_id, bot_file)
    write_trade_to_csv(order, filepath)
    update_portfolio(order, portfolio_path)

# === Live Trade Logic ===
def send_live_order(order):
    print("🚀 Sending live order to exchange:")
    print(json.dumps(order, indent=2))

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

        # Update live portfolio
        user_id = order["user_id"]
        portfolio_path = get_portfolio_path(user_id, "live")
        log_trade(order, "live", portfolio_path, user_id)

    except Exception as e:
        print(f"❌ Error placing Kraken order: {e}")

# === Portfolio Update (Paper & Live) ===
def update_portfolio(order, path):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump({"USD": 0.0}, f, indent=2)

    with open(path, 'r') as f:
        portfolio = json.load(f)

    coin = order['coin']
    action = order['action']
    amount = float(order['amount'])
    price = float(order['price'])

    portfolio.setdefault(coin, 0.0)

    if action == "buy":
        cost = amount * price
        if portfolio.get("USD", 0) >= cost:
            portfolio["USD"] -= cost
            portfolio[coin] += amount
    elif action == "sell":
        if portfolio.get(coin, 0) >= amount:
            proceeds = amount * price
            portfolio["USD"] += proceeds
            portfolio[coin] -= amount

    with open(path, 'w') as f:
        json.dump(portfolio, f, indent=2)
