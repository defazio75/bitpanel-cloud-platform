import os
import json
from datetime import datetime
from config.config import get_mode
from utils.trade_executor import execute_trade
from utils.account_summary import get_total_portfolio_value
from utils.config_loader import get_setting
from utils.state_loader import load_strategy_allocations
from utils.kraken_wrapper import get_live_balances, get_live_prices
from utils.paper_reset import load_paper_balances
from utils.performance_logger import log_trade_multi

COIN = "BTC"
STRATEGY = "RSI_5MIN"

# === Load coin state ===
def load_coin_state(coin, mode="paper"):
    path = f"data/json_{mode}/current/{coin}_state.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

# === Save updated bot state ===
def save_bot_state(coin, strategy, new_state, mode="paper"):
    path = f"data/json_{mode}/current/{coin}_state.json"
    full_state = load_coin_state(coin, mode)
    full_state[strategy] = new_state
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(full_state, f, indent=2)

# === Calculate allocation ===
def calculate_btc_allocation(price, allocation_pct, mode):
    portfolio_value = get_total_portfolio_value(mode)
    allocated_usd = (allocation_pct / 100) * portfolio_value
    return allocated_usd / price if price else 0

# === Update profit log ===
def update_profit_json(coin, mode, coin_amount, profit_usd):
    path = os.path.join(f"json_{mode}", "performance", f"{coin.lower()}_profits.json")
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
                "rsi_5min": {
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

    bot_stats = data.get("bots", {}).get("rsi_5min", {})
    bot_stats[f"{coin.lower()}_accumulated"] = bot_stats.get(f"{coin.lower()}_accumulated", 0.0) + coin_amount
    bot_stats["profit_usd"] = bot_stats.get("profit_usd", 0.0) + profit_usd
    bot_stats["trades"] = bot_stats.get("trades", 0) + 1
    data["bots"]["rsi_5min"] = bot_stats

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# === Main Bot Run ===
def run(price_data, coin="BTC", mode=None):
    if not mode:
        mode = get_mode()
        print(f"🚨 Running in {mode.upper()} MODE")

    bot_name = f"rsi_5min_{coin.lower()}"
    state = load_coin_state(coin, mode).get(STRATEGY, {})
    allocation_pct = load_strategy_allocations(mode).get(coin, {}).get(STRATEGY, 0)

    if allocation_pct <= 0:
        print(f"⚠️ No allocation set for {bot_name}. Clearing state and skipping.")
        state = {
            "status": "Inactive",
            "amount": 0.0,
            "buy_price": 0.0,
            "usd_held": 0.0
        }
        save_bot_state(coin, STRATEGY, state, mode)
        return

    cur_price = price_data.get("price")
    rsi_value = price_data.get("rsi")

    # === Auto-initialize from existing BTC if no state ===
    if not state:
        balances = get_live_balances() if mode == "live" else load_paper_balances()
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
                coin=coin,
                strategy="RSI_5MIN",
                action="buy",
                amount=held,
                price=cur_price,
                mode=mode,
                notes="Assigned BTC to RSI_5MIN strategy (virtual entry)"
            )
        else:
            state = {
                "status": "none",
                "amount": 0.0,
                "buy_price": 0.0
            }

    # === Buy Condition ===
    if state["status"] == "none" and rsi_value < 30:
        coin_amount = calculate_btc_allocation(cur_price, allocation_pct, mode)
        if coin_amount > 0:
            execute_trade(bot_name, "buy", coin_amount, cur_price, mode, coin)

            # Log the entry
            from utils.performance_logger import log_trade_multi
            log_trade_multi(
                coin=coin,
                strategy="RSI_5MIN",
                action="buy",
                amount=coin_amount,
                price=cur_price,
                mode=mode,
                notes="RSI < 30 triggered entry"
            )

            state.update({
                "status": "Holding",
                "amount": coin_amount,
                "buy_price": cur_price
            })

    # === Sell Condition ===
    elif state["status"] == "Holding" and rsi_value > 70:
        coin_amount = state.get("amount", 0.0)
        buy_price = state.get("buy_price", 0.0)
        cur_price = price_data["price"]
        only_sell_profit = get_setting("only_sell_in_profit", "rsi_5min")
        min_profit_usd = 1.00  # Optional: only sell if profit > $1.00

        profit_usd = (cur_price - buy_price) * coin_amount
        is_profitable = profit_usd > min_profit_usd

        if coin_amount > 0 and (not only_sell_profit or is_profitable):
            execute_trade(bot_name, "sell", coin_amount, cur_price, mode, coin)
            update_profit_json(coin, mode, coin_amount, profit_usd)

            # NEW: Log to all timeframes
            from utils.performance_logger import log_trade_multi
            log_trade_multi(
                coin=coin,
                strategy="RSI_5MIN",
                action="sell",
                amount=coin_amount,
                price=cur_price,
                mode=mode,
                profit_usd=profit_usd,
                notes="Exited on RSI > 70"
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

    save_bot_state(coin, STRATEGY, state, mode)
    print(f"💾 {bot_name} state saved: {state}")

if __name__ == "__main__":
    run({"price": 62000, "rsi": 28})
