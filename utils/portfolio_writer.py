import os
import pandas as pd
from datetime import datetime
from utils.config import get_mode
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.firebase_db import (
    save_portfolio_snapshot,
    save_coin_state,
    load_coin_state,
)


def write_portfolio_snapshot(user_id, mode=None, token=None):
    if not mode:
        mode = get_mode(user_id)

    prices = get_prices(user_id=user_id)
    balances = get_live_balances(user_id=user_id)

    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "usd_balance": 0.0,
        "coins": {},
        "total_usd": 0.0
    }

    for coin in balances:
        coin_upper = coin.upper()
        price = prices.get(coin_upper, 0.0)
        state = load_coin_state(user_id, coin, token, mode)
        balance = 0.0

        # Sum coin amounts from all strategies + HODL
        for strat in ["HODL", "RSI_5MIN", "RSI_1HR", "BOLLINGER", "DCA MATRIX"]:
            if strat in state:
                balance += float(state[strat].get("amount", 0.0))
                snapshot["usd_balance"] += float(state[strat].get("usd_held", 0.0))

        value = round(balance * price, 2)
        snapshot["coins"][coin_upper] = {
            "balance": round(balance, 6),
            "price": round(price, 2),
            "value": value
        }

        snapshot["total_usd"] += value

    snapshot["total_usd"] += snapshot["usd_balance"]

    save_portfolio_snapshot(user_id=user_id, snapshot=snapshot, token=token, mode=mode)
    print(f"✅ Portfolio snapshot updated for {user_id} — Total USD: ${snapshot['total_usd']:.2f}")
