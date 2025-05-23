import json
import os
import csv
from datetime import datetime
from config.config import get_mode
from utils.kraken_wrapper import rate_limited_query_private, get_prices
import json
import os
import csv
from datetime import datetime
from config.config import get_mode
from utils.kraken_wrapper import rate_limited_query_private, get_prices
from utils.performance_logger import log_execution_event

TRADE_LOG_PATH = os.path.join("data", "logs", "paper", "paper_trade_log.json")
PORTFOLIO_PATH = os.path.join("data", "logs", "paper", "paper_portfolio.json")
LIVE_LOG_PATH = os.path.join("data", "logs", "live", "live_trade_log.json")
LIVE_PORTFOLIO_PATH = os.path.join("data", "logs", "live", "live_portfolio.json")

def execute_trade(bot_name, action, amount, price, mode=None, coin="BTC"):
    if not mode:
        mode = get_mode()

    log_folder = os.path.join("data", "logs", mode)
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, "trade_log.csv")

    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "bot_name", "coin", "action", "price", "amount", "mode"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "bot_name": bot_name,
            "coin": coin,
            "action": action,
            "price": round(price, 2),
            "amount": round(amount, 6),
            "mode": mode
        })

    print(f"📝 [{bot_name.upper()}] {action.upper()} {round(amount,6)} {coin} @ ${price:,.2f}")

    # === NEW: Log and simulate execution ===
    order = {
        "bot_name": bot_name,
        "coin": coin,
        "action": action,
        "price": round(price, 2),
        "amount": round(amount, 6),
        "mode": mode
    }

    if mode == "paper":
        log_paper_trade(order)
    else:
        send_live_order(order)

def write_trade_log(trade, mode):
    """
    Write a trade entry to the trade log CSV.
    """
    log_folder = os.path.join("data", "logs", mode)
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, "trade_log.csv")

    trade["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    fieldnames = [
        "timestamp",
        "bot_name",
        "coin",
        "action",
        "price",
        "amount",
        "mode"
    ]

    file_exists = os.path.exists(log_path)

    with open(log_path, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade)

def log_paper_trade(order_details):
    bot_name = order_details.get("bot_name", "unknown").lower()
    base_bot_name = bot_name.split("_")[0]  # e.g., 'rsi', 'dca', 'bollinger'
    log_folder = os.path.join("data", "logs", "paper")
    os.makedirs(log_folder, exist_ok=True)

    log_path = os.path.join(log_folder, f"{base_bot_name}_trades.csv")

    file_exists = os.path.exists(log_path)

    with open(log_path, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "bot_name", "coin", "action", "price", "amount", "mode"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "bot_name": order_details["bot_name"],
            "coin": order_details["coin"],
            "action": order_details["action"],
            "price": round(order_details["price"], 2),
            "amount": round(order_details["amount"], 6),
            "mode": order_details["mode"]
        })

    update_paper_portfolio(order_details)

def log_live_trade(order_details):
    bot_name = order_details.get("bot_name", "unknown").lower()
    base_bot_name = bot_name.split("_")[0]
    log_folder = os.path.join("data", "logs", "live")
    os.makedirs(log_folder, exist_ok=True)

    log_path = os.path.join(log_folder, f"{base_bot_name}_trades.csv")

    file_exists = os.path.exists(log_path)

    with open(log_path, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "bot_name", "coin", "action", "price", "amount", "mode"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "bot_name": order_details["bot_name"],
            "coin": order_details["coin"],
            "action": order_details["action"],
            "price": round(order_details["price"], 2),
            "amount": round(order_details["amount"], 6),
            "mode": order_details["mode"]
        })

    update_live_portfolio(order_details)

def update_paper_portfolio(order):
    if not os.path.exists(PORTFOLIO_PATH):
        print("⚠️ No paper portfolio found.")
        return

    with open(PORTFOLIO_PATH, 'r') as f:
        portfolio = json.load(f)

    coin = order['coin']
    action = order['action']
    amount = float(order['amount'])
    price = float(order['price'])

    if coin not in portfolio:
        portfolio[coin] = 0.0

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

    with open(PORTFOLIO_PATH, 'w') as f:
        json.dump(portfolio, f, indent=2)

def update_live_portfolio(order):
    if not os.path.exists(LIVE_PORTFOLIO_PATH):
        print("⚠️ No live portfolio found. Creating new one.")
        with open(LIVE_PORTFOLIO_PATH, 'w') as f:
            json.dump({"USD": 0.0}, f, indent=2)

    with open(LIVE_PORTFOLIO_PATH, 'r') as f:
        portfolio = json.load(f)

    coin = order['coin']
    action = order['action']
    amount = float(order['amount'])
    price = float(order['price'])

    if coin not in portfolio:
        portfolio[coin] = 0.0

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

    with open(LIVE_PORTFOLIO_PATH, 'w') as f:
        json.dump(portfolio, f, indent=2)

def send_live_order(order_details):
    print("🚀 Sending live order to exchange:")
    print(json.dumps(order_details, indent=2))

    try:
        coin = order_details["coin"]
        side = order_details["action"]
        volume = order_details["amount"]
        pair_map = {
            "BTC": "XXBTZUSD",
            "ETH": "XETHZUSD",
            "SOL": "SOLUSD",
            "XRP": "XXRPZUSD",
            "DOT": "DOTUSD",
            "LINK": "LINKUSD"
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

        # Only log if order succeeded
        log_live_trade(order_details)

    except Exception as e:
        print(f"❌ Error placing Kraken order: {e}")

TRADE_LOG_PATH = os.path.join("data", "logs", "paper", "paper_trade_log.json")
PORTFOLIO_PATH = os.path.join("data", "logs", "paper", "paper_portfolio.json")
LIVE_LOG_PATH = os.path.join("data", "logs", "live", "live_trade_log.json")
LIVE_PORTFOLIO_PATH = os.path.join("data", "logs", "live", "live_portfolio.json")

def execute_trade(bot_name, action, amount, price, mode=None, coin="BTC"):
    if not mode:
        mode = get_mode()

    log_folder = os.path.join("data", "logs", mode)
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, "trade_log.csv")

    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "bot_name", "coin", "action", "price", "amount", "mode"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "bot_name": bot_name,
            "coin": coin,
            "action": action,
            "price": round(price, 2),
            "amount": round(amount, 6),
            "mode": mode
        })

    print(f"📝 [{bot_name.upper()}] {action.upper()} {round(amount,6)} {coin} @ ${price:,.2f}")

    # ✅ Log internal execution event
    log_execution_event(
        bot_name=bot_name,
        action=action,
        coin=coin,
        amount=amount,
        price=price,
        mode=mode,
        message="Executed via execute_trade()"
    )

    # === NEW: Log and simulate execution ===
    order = {
        "bot_name": bot_name,
        "coin": coin,
        "action": action,
        "price": round(price, 2),
        "amount": round(amount, 6),
        "mode": mode
    }

    if mode == "paper":
        log_paper_trade(order)
    else:
        send_live_order(order)

def write_trade_log(trade, mode):
    """
    Write a trade entry to the trade log CSV.
    """
    log_folder = os.path.join("data", "logs", mode)
    os.makedirs(log_folder, exist_ok=True)
    log_path = os.path.join(log_folder, "trade_log.csv")

    trade["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    fieldnames = [
        "timestamp",
        "bot_name",
        "coin",
        "action",
        "price",
        "amount",
        "mode"
    ]

    file_exists = os.path.exists(log_path)

    with open(log_path, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade)

def log_paper_trade(order_details):
    bot_name = order_details.get("bot_name", "unknown").lower()
    base_bot_name = bot_name.split("_")[0]  # e.g., 'rsi', 'dca', 'bollinger'
    log_folder = os.path.join("data", "logs", "paper")
    os.makedirs(log_folder, exist_ok=True)

    log_path = os.path.join(log_folder, f"{base_bot_name}_trades.csv")

    file_exists = os.path.exists(log_path)

    with open(log_path, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "bot_name", "coin", "action", "price", "amount", "mode"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "bot_name": order_details["bot_name"],
            "coin": order_details["coin"],
            "action": order_details["action"],
            "price": round(order_details["price"], 2),
            "amount": round(order_details["amount"], 6),
            "mode": order_details["mode"]
        })

    update_paper_portfolio(order_details)

def log_live_trade(order_details):
    bot_name = order_details.get("bot_name", "unknown").lower()
    base_bot_name = bot_name.split("_")[0]
    log_folder = os.path.join("data", "logs", "live")
    os.makedirs(log_folder, exist_ok=True)

    log_path = os.path.join(log_folder, f"{base_bot_name}_trades.csv")

    file_exists = os.path.exists(log_path)

    with open(log_path, "a", newline="") as csvfile:
        fieldnames = ["timestamp", "bot_name", "coin", "action", "price", "amount", "mode"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "bot_name": order_details["bot_name"],
            "coin": order_details["coin"],
            "action": order_details["action"],
            "price": round(order_details["price"], 2),
            "amount": round(order_details["amount"], 6),
            "mode": order_details["mode"]
        })

    update_live_portfolio(order_details)

def update_paper_portfolio(order):
    if not os.path.exists(PORTFOLIO_PATH):
        print("⚠️ No paper portfolio found.")
        return

    with open(PORTFOLIO_PATH, 'r') as f:
        portfolio = json.load(f)

    coin = order['coin']
    action = order['action']
    amount = float(order['amount'])
    price = float(order['price'])

    if coin not in portfolio:
        portfolio[coin] = 0.0

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

    with open(PORTFOLIO_PATH, 'w') as f:
        json.dump(portfolio, f, indent=2)

def update_live_portfolio(order):
    if not os.path.exists(LIVE_PORTFOLIO_PATH):
        print("⚠️ No live portfolio found. Creating new one.")
        with open(LIVE_PORTFOLIO_PATH, 'w') as f:
            json.dump({"USD": 0.0}, f, indent=2)

    with open(LIVE_PORTFOLIO_PATH, 'r') as f:
        portfolio = json.load(f)

    coin = order['coin']
    action = order['action']
    amount = float(order['amount'])
    price = float(order['price'])

    if coin not in portfolio:
        portfolio[coin] = 0.0

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

    with open(LIVE_PORTFOLIO_PATH, 'w') as f:
        json.dump(portfolio, f, indent=2)

def send_live_order(order_details):
    print("🚀 Sending live order to exchange:")
    print(json.dumps(order_details, indent=2))

    try:
        coin = order_details["coin"]
        side = order_details["action"]
        volume = order_details["amount"]
        pair_map = {
            "BTC": "XXBTZUSD",
            "ETH": "XETHZUSD",
            "SOL": "SOLUSD",
            "XRP": "XXRPZUSD",
            "DOT": "DOTUSD",
            "LINK": "LINKUSD"
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

        # Only log if order succeeded
        log_live_trade(order_details)

    except Exception as e:
        print(f"❌ Error placing Kraken order: {e}")