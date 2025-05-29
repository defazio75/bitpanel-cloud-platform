import csv
import os
from datetime import datetime
import requests

def log_trade(user_id, bot_name, action, price, btc_amount, profit=None, portfolio_value=None):
    log_file = os.path.join("data", "logs", user_id, "trade_log.csv")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_exists = os.path.isfile(log_file)

    with open(log_file, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow([
                'timestamp',
                'bot_name',
                'action',
                'price',
                'btc_amount',
                'usd_value',
                'profit',
                'portfolio_value'
            ])

        usd_value = price * btc_amount if btc_amount else 0

        writer.writerow([
            datetime.now().isoformat(),
            bot_name,
            action,
            round(price, 2),
            round(btc_amount, 8),
            round(usd_value, 2),
            round(profit, 2) if profit is not None else '',
            round(portfolio_value, 2) if portfolio_value is not None else ''
        ])

    # Optional: Push notification via ntfy
    try:
        topic = "btc-bot-alerts"
        url = f"https://ntfy.sh/{topic}"
        message = (
            f"{bot_name} just {action.upper()} {round(btc_amount, 8)} BTC\n"
            f"@ ${round(price, 2)} per BTC\n"
            f"Total: ${round(price * btc_amount, 2)}"
        )
        requests.post(url, data=message.encode('utf-8'))
    except Exception as e:
        print(f"[Notification Error] {e}")

def init_log(user_id):
    log_file = os.path.join("data", "logs", user_id, "trade_log.csv")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'timestamp',
                'bot_name',
                'action',
                'price',
                'btc_amount',
                'usd_value',
                'profit',
                'portfolio_value'
            ])
