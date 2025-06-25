from datetime import datetime
from utils.config import get_mode
from utils.kraken_wrapper import get_rsi, get_live_balances, get_prices
from utils.performance_logger import log_trade
from utils.firebase_db import (
    load_strategy_allocations,
    load_portfolio_snapshot,
    load_coin_state,
    save_coin_state, 
    load_portfolio_balances
)

mode = get_mode()
if mode == "live":
    from utils.trade_executor import execute_trade
else:
    from utils.trade_simulator import simulate_trade

STRATEGY = "1Hr RSI"
RSI_PERIOD = 14
BUY_THRESHOLD = 30
SELL_THRESHOLD = 70
PROFIT_TARGET = 1.03  # 3% profit target

def load_strategy_usd(user_id, coin, strategy_key, mode, token):
    data = load_strategy_allocations(user_id, token, mode) or {}
    return data.get(coin.upper(), {}).get(strategy_key.upper(), 0.0)

# === Main Bot Logic ===
def run(price_data, user_id, coin="BTC", mode=None):
    print(f"🟢 [RSI 1HR] Running for user: {user_id}")
    if not mode:
        mode = get_mode()
    token = st.session_state.user["token"]
    cur_price = price_data.get("price")
    cur_rsi = price_data.get("rsi") or get_rsi(coin, interval="1h", period=RSI_PERIOD)

    state = load_coin_state(user_id, coin, token, mode) or {}
    strat_state = state.get(STRATEGY, {})
    status = strat_state.get("status", "waiting")
    entry_price = strat_state.get("entry_price", 0)
    amount = strat_state.get("amount", 0)

    allocated_usd = load_strategy_usd(user_id, coin, STRATEGY, mode, token)
    if allocated_usd <= 0:
        print(f"⚠️ No USD allocation set for {STRATEGY}. Exiting.")
        return

    if mode == "live":
        balances = get_live_balances(user_id)
    else:
        portfolio_data = load_portfolio_snapshot(user_id, token, mode) or {}
        balances = portfolio_data.get("balances", {})

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
    save_coin_state(user_id, coin, state, token, mode)
    print(f"💾 {bot_name} state saved: {state}")
