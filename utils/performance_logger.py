import os
import csv
from datetime import datetime
from utils.config import get_mode

# === Shared CSV Writer ===
def write_log_row(file_path, headers, row):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

# === Trade Logger (Daily/Weekly/Monthly/Yearly) ===
def log_trade_trade(user_id, coin, strategy, action, amount, price, mode=None, profit_usd=0.0, notes=""):
    if not user_id:
        raise ValueError("❌ user_id is required for logging trades.")

    if not mode:
        mode = get_mode(user_id)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    usd_value = round(amount * price, 2)
    profit_usd = round(profit_usd, 2)
    date_str = now.strftime("%Y-%m-%d")
    week_str = now.strftime("%Y-W%U")
    month_str = now.strftime("%Y-%m")
    year_str = now.strftime("%Y")

    base_path = os.path.join("data", "logs", mode, user_id)

    headers = ["Timestamp", "Coin", "Strategy", "Action", "Amount", "Price", "USD Value", "P/L ($)", "Notes"]
    row = [timestamp, coin, strategy, action, round(amount, 6), round(price, 2), usd_value, profit_usd, notes]

    write_log_row(os.path.join(base_path, "daily", f"{date_str}_trade_log.csv"), headers, row)
    write_log_row(os.path.join(base_path, "weekly", f"{week_str}_week_log.csv"), headers, row)
    write_log_row(os.path.join(base_path, "monthly", f"{month_str}_month_log.csv"), headers, row)
    write_log_row(os.path.join(base_path, "yearly", f"{year_str}_year_log.csv"), headers, row)

    print(f"📝 Trade logged → {action.upper()} {coin} | {strategy} | ${usd_value} @ {price}")

# === DCA Logger (Same as Above) ===
def log_dca_trade(user_id, coin, action, amount, price, mode=None, notes=""):
    if not user_id:
        raise ValueError("❌ user_id is required for logging DCA trades.")

    if not mode:
        mode = get_mode(user_id)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    usd_value = round(amount * price, 2)
    date_str = now.strftime("%Y-%m-%d")
    week_str = now.strftime("%Y-W%U")
    month_str = now.strftime("%Y-%m")
    year_str = now.strftime("%Y")

    base_path = os.path.join("data", "logs", mode, user_id, "dca")

def log_execution_event(user_id, message, mode=None):
    if not mode:
        mode = get_mode(user_id)

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.join("data", "logs", mode, user_id, "execution_log.csv")
    headers = ["Timestamp", "Message"]
    row = [timestamp, message]

    write_log_row(log_path, headers, row)
    print(f"⚙️ Execution Event Logged: {message}")

    headers = ["Timestamp", "Coin", "Action", "Amount", "Price", "USD Value", "Notes"]
    row = [timestamp, coin, action, round(amount, 6), round(price, 2), usd_value, notes]
    write_log_row(os.path.join(base_path, "daily", f"{date_str}_dca_log.csv"), headers, row)
