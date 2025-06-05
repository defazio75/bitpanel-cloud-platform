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

    # === Adjust balances ===
    coin_key = coin.upper()
    current_balance = snapshot.get("coins", {}).get(coin_key, {}).get("balance", 0.0)

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

    # === Update coin balance in snapshot ===
    snapshot["coins"][coin_key] = {
        "balance": new_balance,
        "price": price,
        "value": round(new_balance * price, 2)
    }

    # === Save updated snapshot ===
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

    # === Optional: Update strategy state ===
    state = load_coin_state(user_id=user_id, coin=coin_key, token=token, mode=mode)
    strategy_key = "HODL"
    strat_block = state.get(strategy_key, {
        "amount": 0,
        "usd_held": 0,
        "status": "Inactive",
        "buy_price": 0,
        "target_usd": 0
    })

    # Update amount
    old_amt = strat_block.get("amount", 0)
    new_amt = round(old_amt + amount, 8) if action == "buy" else round(old_amt - amount, 8)
    strat_block["amount"] = new_amt

    # Update USD held
    old_usd = strat_block.get("usd_held", 0)
    new_usd = round(old_usd - usd_value, 2) if action == "buy" else round(old_usd + usd_value, 2)
    strat_block["usd_held"] = new_usd

    # Set strategy status
    strat_block["status"] = "Active" if new_amt > 0 or new_usd > 0 else "Inactive"

    # Set/update buy_price ONLY on buy
    if action == "buy" and amount > 0:
        strat_block["buy_price"] = price

    state[strategy_key] = strat_block
    save_coin_state(user_id=user_id, coin=coin_key, state_data=state, token=token, mode=mode)
    print(f"📦 Updated {coin_key} strategy state for {strategy_key}.")
