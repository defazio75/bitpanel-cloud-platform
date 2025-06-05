import os
import json
import streamlit as st
from datetime import datetime
from utils.logger import log_trade_multi
from utils.config import get_mode
from utils.kraken_wrapper import get_prices
from utils.firebase_db import (
    save_portfolio_snapshot,
    load_portfolio_snapshot,
    save_coin_state,
    load_coin_state
)


def simulate_trade(user_id, coin, action, amount, price=None):
    mode = get_mode(user_id)
    token = st.session_state.get("token")

    # === Load current snapshot ===
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    prices = get_prices(user_id=user_id)
    price = price or prices.get(coin.upper(), 0)
    usd_value = round(amount * price, 2)

    if "coins" not in snapshot:
        snapshot["coins"] = {}

    # === Adjust balances ===
    coin_key = coin.upper()
    current_balance = snapshot.get("coins", {}).get(coin_key, {}).get("balance", 0.0)

    if action == "buy":
        if snapshot.get("usd_balance", 0) < usd_value:
            print(f"❌ Not enough USD to simulate buy of {amount} {coin_key}.")
            return
        snapshot["usd_balance"] = round(snapshot["usd_balance"] - usd_value, 2)
        new_balance = round(current_balance + amount, 8)

    elif action == "sell":
        if current_balance < amount:
            print(f"❌ Not enough {coin_key} to simulate sell of {amount}.")
            return
        snapshot["usd_balance"] = round(snapshot.get("usd_balance", 0) + usd_value, 2)
        new_balance = round(current_balance - amount, 8)

    else:
        print("❌ Invalid action. Must be 'buy' or 'sell'.")
        return

    # === Update snapshot ===
    snapshot["coins"][coin_key] = {
        "balance": new_balance,
        "price": price,
        "value": round(new_balance * price, 2)
    }
    snapshot["total_value"] = round(
        snapshot["usd_balance"] + sum(c["value"] for c in snapshot["coins"].values()), 2
    )
    snapshot["timestamp"] = datetime.utcnow().isoformat()
    save_portfolio_snapshot(user_id, snapshot, token, mode)

    # === Log trade ===
    log_trade_multi(
        user_id=user_id,
        coin=coin_key,
        strategy="HODL",
        action=action,
        amount=amount,
        price=price,
        mode=mode,
        notes="Simulated trade"
    )

    # === Update HODL state ===
    state = load_coin_state(user_id=user_id, coin=coin_key, token=token, mode=mode)
    hodl_block = state.get("HODL", {})

    if action == "buy":
        hodl_block["amount"] = round(hodl_block.get("amount", 0) + amount, 8)
        hodl_block["buy_price"] = price
        hodl_block["status"] = "Active"
    elif action == "sell":
        new_amt = round(hodl_block.get("amount", 0) - amount, 8)
        hodl_block["amount"] = max(new_amt, 0)
        hodl_block["status"] = "Active" if new_amt > 0 else "Inactive"

    hodl_block["timestamp"] = datetime.utcnow().isoformat()
    state["HODL"] = hodl_block
    save_coin_state(user_id=user_id, coin=coin_key, state_data=state, token=token, mode=mode)

    print(f"📦 Updated {coin_key} HODL state.")
