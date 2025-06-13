from datetime import datetime
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.performance_logger import log_trade
from utils.firebase_db import (
    load_strategy_allocations,
    load_portfolio_snapshot,
    load_coin_state,
    save_coin_state, 
    load_balances
)
from utils.config import get_mode

mode = get_mode()
if mode == "live":
    from utils.trade_executor import execute_trade
else:
    from utils.trade_simulator import simulate_trade

STRATEGY = "Bollinger"

def load_strategy_usd(user_id, coin, strategy_key, mode, token):
    data = load_strategy_allocations(user_id, token, mode) or {}

def calculate_btc_allocation(price, allocated_usd):
    return 0 if price == 0 else allocated_usd / price

def update_profit_json(user_id, coin, mode, coin_amount, profit_usd, token):
    path = f"{mode}/performance/by_bot/BOLLINGER.json"
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
    print(f"🟢 [BOLLINGER] Running for user: {user_id}")
    if not mode:
        mode = get_mode()
    token = st.session_state.user["token"]
    bot_name = f"bollinger_breakout_{coin.lower()}"

    state = load_coin_state(user_id, coin, token, mode) or {}

    allocated_usd = load_strategy_usd(user_id, coin, STRATEGY, mode, token)
    if allocated_usd <= 0:
        print(f"⚠️ No USD allocation set for {bot_name}. Clearing state and skipping.")
        state = {
            "status": "Inactive",
            "amount": 0.0,
            "buy_price": 0.0,
            "usd_held": 0.0
        }
        save_coin_state(user_id, coin, state, token, mode)
        return

    cur_price = price_data.get("price")
    band_upper = price_data.get("band_upper")
    band_lower = price_data.get("band_lower")
    only_sell_profit = get_setting("only_sell_in_profit", "bollinger_breakout")

    # === Auto-initialize from existing BTC if no state ===
    if not state:
        portfolio_data = load_portfolio_snapshot(user_id, token, mode) or {}
        balances = portfolio_data.get("balances", {})
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
                notes="Assigned BTC to BOLLINGER strategy (virtual entry)"
            )
        else:
            state = {
                "status": "none",
                "amount": 0.0,
                "buy_price": 0.0
            }

    # === Buy Logic ===
    if state["status"] == "none" and cur_price < band_lower:
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
                notes="BB lower band breakout entry"
            )

            state.update({
                "status": "Holding",
                "amount": coin_amount,
                "buy_price": cur_price
            })

    # === Sell Logic ===
    elif state["status"] == "Holding" and cur_price > band_upper:
        coin_amount = state.get("amount", 0.0)
        buy_price = state.get("buy_price", 0.0)
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
                notes="Exited at BB upper band"
            )

            state.update({
                "status": "none",
                "amount": 0.0,
                "buy_price": 0.0,
                "usd_held": round(coin_amount * cur_price, 2)
            })

            print(f"✅ {bot_name} SOLD {coin_amount:.6f} {coin} at ${cur_price:.2f} for ${profit_usd:.2f} profit.")
        else:
            print(f"⚠️ {bot_name} breakout triggered, but profit condition not met. P/L: ${profit_usd:.2f}")

    save_coin_state(user_id, coin, state, token, mode)
    print(f"💾 {bot_name} state saved: {state}")
