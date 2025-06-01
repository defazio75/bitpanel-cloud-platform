from datetime import datetime
from utils.config import get_mode
from utils.trade_executor import execute_trade
from utils.account_summary import get_total_portfolio_value
from utils.config_loader import get_setting
from utils.kraken_wrapper import get_live_balances, get_live_prices
from utils.performance_logger import log_trade_multi
from utils.firebase_db import load_firebase_json, save_firebase_json
import streamlit as st

STRATEGY = "RSI_1HR"

def load_strategy_usd(user_id, coin, strategy_key, mode, token):
    path = f"{mode}/allocations/strategy_allocations.json"
    data = load_firebase_json(path, user_id, token) or {}
    return data.get(coin.upper(), {}).get(strategy_key.upper(), 0.0)

def calculate_btc_allocation(price, allocated_usd):
    return 0 if price == 0 else allocated_usd / price

def update_profit_json(user_id, coin, mode, coin_amount, profit_usd, token):
    path = f"{mode}/performance/by_bot/RSI_1HR.json"
    data = load_firebase_json(path, user_id, token) or {
        f"{coin}_accumulated": 0.0,
        "profit_usd": 0.0,
        "trades": 0,
        "last_trade_time": None
    }

    data[f"{coin}_accumulated"] += coin_amount
    data["profit_usd"] += profit_usd
    data["trades"] += 1
    data["last_trade_time"] = datetime.utcnow().isoformat()

    save_firebase_json(path, data, user_id, token)

def run(price_data, user_id, coin="BTC", mode=None):
    """
    1-Hour RSI Strategy Bot — Firebase-integrated
    """
    if not mode:
        mode = get_mode()
        print(f"🚨 Running in {mode.upper()} MODE")

    token = st.session_state.user["token"]
    bot_name = f"rsi_1hr_{coin.lower()}"

    # Load state from Firebase
    state_path = f"{mode}/current/{coin}/{STRATEGY}.json"
    state = load_firebase_json(state_path, user_id, token) or {}

    allocated_usd = load_strategy_usd(user_id, coin, STRATEGY, mode, token)
    if allocated_usd <= 0:
        print(f"⚠️ No USD allocation set for {bot_name}. Clearing state and skipping.")
        state = {
            "status": "Inactive",
            "amount": 0.0,
            "buy_price": 0.0,
            "usd_held": 0.0
        }
        save_firebase_json(state_path, state, user_id, token)
        return

    cur_price = price_data.get("price")
    rsi_value = price_data.get("rsi")

    # Auto-initialize from held balance
    if not state:
        balances = get_live_balances(user_id) if mode == "live" else load_paper_balances(user_id)
        held = balances.get(coin.upper(), 0)
        if held > 0 and cur_price > 0:
            print(f"🔄 Initializing {bot_name} as Holding — {held:.6f} {coin} detected in account.")
            state = {
                "status": "Holding",
                "amount": held,
                "buy_price": cur_price
            }

            log_trade_multi(
                user_id=user_id,
                coin=coin,
                strategy=STRATEGY,
                action="buy",
                amount=held,
                price=cur_price,
                mode=mode,
                notes="Assigned BTC to RSI_1HR strategy (virtual entry)"
            )
        else:
            state = {
                "status": "none",
                "amount": 0.0,
                "buy_price": 0.0
            }

    # === Buy Logic ===
    if state["status"] == "none" and rsi_value < 30:
        coin_amount = calculate_btc_allocation(cur_price, allocated_usd)
        if coin_amount > 0:
            execute_trade(bot_name, "buy", coin_amount, cur_price, mode, coin)

            log_trade_multi(
                user_id=user_id,
                coin=coin,
                strategy=STRATEGY,
                action="buy",
                amount=coin_amount,
                price=cur_price,
                mode=mode,
                notes="RSI dipped below 30 — buy signal"
            )

            state.update({
                "status": "Holding",
                "amount": coin_amount,
                "buy_price": cur_price
            })

    # === Sell Logic ===
    elif state["status"] == "Holding" and rsi_value > 70:
        coin_amount = state.get("amount", 0.0)
        buy_price = state.get("buy_price", 0.0)
        only_sell_profit = get_setting("only_sell_in_profit", "rsi_1hr")

        profit_usd = (cur_price - buy_price) * coin_amount
        is_profitable = profit_usd > 1.00

        if coin_amount > 0 and (not only_sell_profit or is_profitable):
            execute_trade(bot_name, "sell", coin_amount, cur_price, mode, coin)
            update_profit_json(user_id, coin, mode, coin_amount, profit_usd, token)

            log_trade_multi(
                user_id=user_id,
                coin=coin,
                strategy=STRATEGY,
                action="sell",
                amount=coin_amount,
                price=cur_price,
                mode=mode,
                profit_usd=profit_usd,
                notes="RSI crossed above 70 — sell signal"
            )

            state.update({
                "status": "none",
                "amount": 0.0,
                "buy_price": 0.0,
                "usd_held": round(coin_amount * cur_price, 2)
            })
            print(f"✅ {bot_name} SOLD {coin_amount:.6f} {coin} at ${cur_price:.2f} for ${profit_usd:.2f} profit.")
        else:
            print(f"⚠️ {bot_name} skipped sell — RSI > 70 but profit condition not met. P/L: ${profit_usd:.2f}")

    # Save updated state
    save_firebase_json(state_path, state, user_id, token)
    print(f"💾 {bot_name} state saved: {state}")
