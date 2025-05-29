# bots/rsi_1hr.py

import os
import json
from datetime import datetime
from config.config import get_mode
from utils.trade_executor import execute_trade
from utils.account_summary import get_total_portfolio_value
from utils.config_loader import get_setting
from utils.kraken_wrapper import get_live_balances, get_live_prices
from utils.paper_reset import load_paper_balances
from utils.performance_logger import log_trade_multi

STRATEGY = "RSI_1HR"

def load_strategy_allocation(user_id, coin, strategy_name, mode):
    path = f"data/json_{mode}/{user_id}/current/{coin}_state.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return data.get(strategy_name, 0)
    return 0

def run(price_data, user_id, coin="BTC", mode=None):
    """
    1-Hour RSI Strategy Bot
    Args:
        price_data: dict - {'price': float, 'rsi': float}
        allocation_data: dict from allocations.json
        coin: "BTC", "ETH", etc.
        mode: "paper" or "live" (if None, auto-load)
    """

    if not mode:
        mode = get_mode()
        print(f"🚨 Running in {mode.upper()} MODE")

    bot_name = f"rsi_1hr_{coin.lower()}"
    state = load_coin_state(user_id, coin, mode).get('RSI_1HR', {})
    allocation_pct = load_strategy_allocation(user_id, coin, "RSI 1-Hour", mode)

    if allocation_pct <= 0:
        print(f"⚠️ No allocation set for {bot_name}. Clearing state and skipping.")
        state = {
            "status": "Inactive",
            "amount": 0.0,
            "buy_price": 0.0,
            "usd_held": 0.0
        }
        save_bot_state(user_id, coin, STRATEGY, state, mode)
        return

    cur_price = price_data.get("price")
    rsi_value = price_data.get("rsi")

    # === Auto-initialize from existing BTC if no state ===
    if not state:
        balances = get_live_balances(user_id) if mode == "live" else load_paper_balances(user_id)
        prices = get_live_prices() if mode == "live" else price_data
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
                strategy="RSI_1HR",
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

    # === Trading Logic ===
    if state["status"] == "none" and rsi_value < 30:
        coin_amount = calculate_btc_allocation(cur_price, allocation_pct, user_id, mode)
        if coin_amount > 0:
            execute_trade(bot_name, "buy", coin_amount, cur_price, mode, coin)
            state.update({
                "status": "Holding",
                "amount": coin_amount,
                "buy_price": cur_price
            })

    elif state["status"] == "Holding" and rsi_value > 70:
        coin_amount = state.get("amount", 0.0)
        buy_price = state.get("buy_price", 0.0)
        cur_price = price_data["price"]
        only_sell_profit = get_setting("only_sell_in_profit", "rsi_1hr")
        min_profit_usd = 1.00  # Optional: only sell if profit > $1.00

        profit_usd = (cur_price - buy_price) * coin_amount
        is_profitable = profit_usd > min_profit_usd

        if coin_amount > 0 and (not only_sell_profit or is_profitable):
            execute_trade(bot_name, "sell", coin_amount, cur_price, mode, coin)
            update_profit_json(user_id, coin, mode, coin_amount, profit_usd)

            state.update({
                "status": "none",
                "amount": 0.0,
                "buy_price": 0.0,
                "usd_held": round(coin_amount * cur_price, 2)
            })
            print(f"✅ {bot_name} SOLD {coin_amount:.6f} {coin} at ${cur_price:.2f} for ${profit_usd:.2f} profit.")
        else:
            print(f"⚠️ {bot_name} skipped sell — RSI > 70 but profit condition not met. P/L: ${profit_usd:.2f}")

        save_bot_state(user_id, coin, STRATEGY, state, mode)
        print(f"💾 {bot_name} state saved: {state}")

    save_bot_state(user_id, coin, STRATEGY, state, mode)
    print(f"💾 {bot_name} state saved: {state}")

def calculate_btc_allocation(price, allocation_pct, user_id, mode):
    portfolio_value = get_total_portfolio_value(user_id, mode)
    allocated_usd = (allocation_pct / 100) * portfolio_value
    if price == 0:
        return 0
    return allocated_usd / price

def update_profit_json(user_id, coin, mode, coin_amount, profit_usd):
    path = os.path.join(f"data/json_{mode}/{user_id}/performance", f"{coin.lower()}_profits.json")
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Profit file not found for {coin.upper()}. Initializing.")
        data = {
            f"total_{coin.lower()}_accumulated": 0.0,
            "total_profit_usd": 0.0,
            "total_trades": 0,
            "last_trade_time": None,
            "bots": {
                "rsi_1hr": {
                    f"{coin.lower()}_accumulated": 0.0,
                    "profit_usd": 0.0,
                    "trades": 0
                }
            }
        }

    data[f"total_{coin.lower()}_accumulated"] += coin_amount
    data["total_profit_usd"] += profit_usd
    data["total_trades"] += 1
    data["last_trade_time"] = datetime.utcnow().isoformat()

    bot_stats = data.get("bots", {}).get("rsi_1hr", {})
    bot_stats[f"{coin.lower()}_accumulated"] = bot_stats.get(f"{coin.lower()}_accumulated", 0.0) + coin_amount
    bot_stats["profit_usd"] = bot_stats.get("profit_usd", 0.0) + profit_usd
    bot_stats["trades"] = bot_stats.get("trades", 0) + 1
    data["bots"]["rsi_1hr"] = bot_stats

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_coin_state(user_id, coin, mode="paper"):
    path = f"data/json_{mode}/{user_id}/current/{coin}_state.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_bot_state(user_id, coin, strategy, new_state, mode="paper"):
    path = f"data/json_{mode}/{user_id}/current/{coin}_state.json"
    full_state = load_coin_state(user_id, coin, mode)
    full_state[strategy] = new_state
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(full_state, f, indent=2)
