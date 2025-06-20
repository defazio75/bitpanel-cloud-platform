from datetime import datetime
from utils.firebase_config import firebase

def log_trade_to_firebase(user_id, mode, trade, token):
    """
    Logs a single trade to Firebase under:
    users/{user_id}/{mode}/trade_logs/{YYYY-MM-DD}/{timestamp}
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H-%M-%S")

    path = (
        firebase.database()
        .child("users")
        .child(user_id)
        .child(mode)
        .child("trade_logs")
        .child(date_str)
        .child(timestamp)
    )

    path.set(trade, token)


def log_trade_multi(
    user_id,
    coin,
    strategy,
    action,
    amount,
    price,
    mode,
    token,
    profit_usd=0.0,
    notes=""
):
    usd_value = round(amount * price, 2)

    trade = {
        "coin": coin,
        "strategy": strategy,
        "action": action,
        "amount": round(amount, 6),
        "price": round(price, 2),
        "usd_value": usd_value,
        "profit": round(profit_usd, 2),
        "notes": notes,
    }

    log_trade_to_firebase(user_id, mode, trade, token)
    print(f"📝 Trade logged: {trade}")
