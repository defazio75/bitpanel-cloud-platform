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

    print(f"✅ Simulated {action} of {amount} {coin_key} at ${price:.2f}.")

    # === Optional: Update strategy state ===
    state = load_coin_state(user_id=user_id, coin=coin_key, token=token, mode=mode)
    strategy_key = "HODL" if "HODL" in state else next(iter(state.keys()), None)
    if strategy_key:
        strat_block = state.get(strategy_key, {})
        # Update amount
        old_amt = strat_block.get("amount", 0)
        strat_block["amount"] = round(old_amt + amount, 8) if action == "buy" else round(old_amt - amount, 8)

        # Update USD held
        old_usd = strat_block.get("usd_held", 0)
        strat_block["usd_held"] = round(old_usd - usd_value, 2) if action == "buy" else round(old_usd + usd_value, 2)

        # ✅ Set strategy status based on holdings
        if strat_block["amount"] > 0 or strat_block["usd_held"] > 0:
            strat_block["status"] = "Active"
        else:
            strat_block["status"] = "Inactive"

        state[strategy_key] = strat_block
        save_coin_state(user_id=user_id, coin=coin_key, state_data=state, token=token, mode=mode)
        print(f"📦 Updated {coin_key} strategy state for {strategy_key}.")

