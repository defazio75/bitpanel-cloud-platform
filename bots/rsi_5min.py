import os
from datetime import datetime
from utils.config import get_mode
from utils.trade_executor import execute_trade
from utils.account_summary import get_total_portfolio_value
from utils.config_loader import get_setting
from utils.state_loader import load_strategy_allocations
from utils.kraken_wrapper import get_live_balances, get_live_prices
from utils.paper_reset import load_paper_balances
from utils.performance_logger import log_trade_multi
from utils.json_utils import load_user_state, save_user_state

STRATEGY = "RSI_5MIN"

# === Calculate allocation ===
def calculate_coin_allocation(price, allocation_pct, user_id, mode):
    portfolio_value = get_total_portfolio_value(user_id, mode)
    allocated_usd = (allocation_pct / 100) * portfolio_value
    return allocated_usd / price if price else 0

# === Main Bot Run ===
def run(price_data, user_id, coin="BTC", mode=None):
    if not mode:
        mode = get_mode()
        print(f"🚨 Running in {mode.upper()} MODE")

    bot_name = f"rsi_5min_{coin.lower()}"

    # === Load full coin state and extract strategy-specific state ===
    full_state = load_user_state(user_id, "current", f"{coin}_state.json", mode) or {}
    state = full_state.get(STRATEGY, {})
    allocation_pct = load_strategy_allocations(user_id, mode).get(coin, {}).get(STRATEGY, 0)

    if allocation_pct <= 0:
        print(f"⚠️ No allocation set for {bot_name}. Clearing state and skipping.")
        state = {
            "status": "Inactive",
            "amount": 0.0,
            "buy_price": 0.0,
            "usd_held": 0.0
        }
        full_state[STRATEGY] = state
        save_user_state(user_id, "current", f"{coin}_state.json", full_state, mode)
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
        coin_amount = calculate_btc_allocation(cur_price, allocation_pct, user_id, mode)
        if coin_amount > 0:
            execute_trade(bot_name, "buy", coin_amount, cur_price, mode, coin, user_id)

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
        only_sell_profit = get_setting("only_sell_in_profit", "rsi_5min")
        min_profit_usd = 1.00

        profit_usd = (cur_price - buy_price) * coin_amount
        is_profitable = profit_usd > min_profit_usd

        if coin_amount > 0 and (not only_sell_profit or is_profitable):
            execute_trade(bot_name, "buy", coin_amount, cur_price, mode, coin, user_id)

            # Log profit to JSON
            profit_path = f"{coin.lower()}_profits.json"
            profit_data = load_user_state(user_id, "performance", profit_path, mode) or {
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

            profit_data[f"total_{coin.lower()}_accumulated"] += coin_amount
            profit_data["total_profit_usd"] += profit_usd
            profit_data["total_trades"] += 1
            profit_data["last_trade_time"] = datetime.utcnow().isoformat()

            bot_stats = profit_data["bots"].get("rsi_5min", {})
            bot_stats[f"{coin.lower()}_accumulated"] += coin_amount
            bot_stats["profit_usd"] += profit_usd
            bot_stats["trades"] += 1
            profit_data["bots"]["rsi_5min"] = bot_stats

            save_user_state(user_id, "performance", profit_path, profit_data, mode)

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

    # === Save updated strategy state ===
    full_state[STRATEGY] = state
    save_user_state(user_id, "current", f"{coin}_state.json", full_state, mode)
    print(f"💾 {bot_name} state saved: {state}")

if __name__ == "__main__":
    run({"price": 62000, "rsi": 28}, user_id="testuser", coin="BTC", mode="paper")
