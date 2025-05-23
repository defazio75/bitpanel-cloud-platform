
import os
import csv
from datetime import datetime

def log_trade_multi(coin, strategy, action, amount, price, mode="paper", profit_usd=0.0, notes=""):
    """
    Logs a trade to daily, weekly, monthly, and yearly CSV files.

    Parameters:
    - coin (str): The coin traded (e.g., 'BTC')
    - strategy (str): The strategy used (e.g., 'RSI_5MIN')
    - action (str): 'buy' or 'sell'
    - amount (float): The crypto amount traded
    - price (float): Price at which trade occurred
    - mode (str): 'paper' or 'live'
    - profit_usd (float): Realized profit in USD (only for sell)
    - notes (str): Optional notes for the trade
    """
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    usd_value = round(amount * price, 2)
    profit_usd = round(profit_usd, 2)
    date_str = now.strftime("%Y-%m-%d")
    week_str = now.strftime("%Y-W%U")
    month_str = now.strftime("%Y-%m")
    year_str = now.strftime("%Y")

    base_path = f"C:/Users/David/Desktop/BitPanel 3.0 Building/data/logs/{mode}"

    def write_log(subfolder, filename):
        folder_path = os.path.join(base_path, subfolder)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, filename)

        file_exists = os.path.isfile(file_path)
        with open(file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow([
                    "Timestamp", "Coin", "Strategy", "Action",
                    "Amount", "Price", "USD Value", "P/L ($)", "Notes"
                ])
            writer.writerow([
                timestamp, coin, strategy, action,
                round(amount, 6), round(price, 2), usd_value, profit_usd, notes
            ])

    write_log("daily", f"{date_str}_trade_log.csv")
    write_log("weekly", f"{week_str}_week_log.csv")
    write_log("monthly", f"{month_str}_month_log.csv")
    write_log("yearly", f"{year_str}_year_log.csv")

    print(f"📝 Trade logged → {action.upper()} {coin} | {strategy} | ${usd_value} @ {price}")

def log_dca_trade(coin, action, amount, price, mode="paper", notes=""):
    """
    Logs a DCA trade to daily, weekly, monthly, and yearly DCA CSV files.

    Parameters:
    - coin (str): The coin bought (e.g., 'BTC')
    - action (str): 'buy' or 'sell' (likely 'buy' only for DCA)
    - amount (float): The crypto amount bought
    - price (float): Price at which trade occurred
    - mode (str): 'paper' or 'live'
    - notes (str): Optional notes for the trade
    """
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    usd_value = round(amount * price, 2)
    date_str = now.strftime("%Y-%m-%d")
    week_str = now.strftime("%Y-W%U")
    month_str = now.strftime("%Y-%m")
    year_str = now.strftime("%Y")

    base_path = f"C:/Users/David/Desktop/BitPanel 3.0 Building/data/logs/{mode}/dca"

    def write_log(subfolder, filename):
        folder_path = os.path.join(base_path, subfolder)
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, filename)

        file_exists = os.path.isfile(file_path)
        with open(file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow([
                    "Timestamp", "Coin", "Action", "Amount", "Price", "USD Value", "Notes"
                ])
            writer.writerow([
                timestamp, coin, action, round(amount, 6), round(price, 2), usd_value, notes
            ])

    write_log("daily", f"{date_str}_dca_log.csv")
    write_log("weekly", f"{week_str}_dca_log.csv")
    write_log("monthly", f"{month_str}_dca_log.csv")
    write_log("yearly", f"{year_str}_dca_log.csv")

    print(f"📥 DCA trade logged → {action.upper()} {coin} | ${usd_value} @ {price}")

def log_execution_event(bot_name, action, coin, amount, price, mode, message=""):
    """
    Logs internal trade execution events for debugging/auditing purposes.

    Parameters:
    - bot_name (str): Name of the bot initiating the trade
    - action (str): 'buy' or 'sell'
    - coin (str): e.g. 'BTC'
    - amount (float): Amount attempted to trade
    - price (float): Trade price
    - mode (str): 'paper' or 'live'
    - message (str): Optional extra message or explanation
    """
    from datetime import datetime
    import os

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    date_str = now.strftime("%Y-%m-%d")

    base_path = f"C:/Users/David/Desktop/BitPanel 3.0 Building/data/logs/{mode}/execution"
    os.makedirs(base_path, exist_ok=True)
    file_path = os.path.join(base_path, f"{date_str}_execution_log.txt")

    log_line = f"[{timestamp}] {bot_name.upper()} | {action.upper()} {coin} | Amount: {amount:.6f} @ ${price:.2f} | {message}\n"

    with open(file_path, "a") as f:
        f.write(log_line)

    print(f"🛠️ EXECUTION LOGGED: {log_line.strip()}")
