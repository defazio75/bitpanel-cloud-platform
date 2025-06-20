from datetime import datetime
from utils.config import get_mode
from utils.kraken_wrapper import get_rsi, get_live_balances, get_prices
from utils.performance_logger import log_trade
from utils.firebase_db import (
    load_strategy_allocations,
    load_portfolio_snapshot,
    load_portfolio_balances,    
    load_coin_state,
    save_coin_state
)

mode = get_mode()
if mode == "live":
    from utils.trade_executor import execute_trade
else:
    from utils.trade_simulator import simulate_trade

STRATEGY = "5min RSI"

def run(user_id, token, coin="BTC"):
    print(f"🟢 [RSI 5MIN] Running for user: {user_id}, Coin: {coin}")
    bot_name = f"{STRATEGY.lower()}_{coin.lower()}"

    # === Fetch price and RSI ===
    print("📡 Fetching live prices and RSI...")
    prices = get_prices(user_id=user_id)
    cur_price = prices.get(coin)
    rsi_value = get_rsi(coin, interval="5min")
    print(f"💰 Price: {cur_price}, 📈 RSI: {rsi_value}")

    if cur_price is None or rsi_value is None:
        print(f"❌ Missing price or RSI for {coin}. Aborting run.")
        return

    # === Load saved state
    print("📂 Loading current coin state...")
    state = load_coin_state(user_id, coin, token, mode) or {}
    strat_state = state.get(STRATEGY, {})

    # === Allocation
    allocated_usd = load_strategy_allocations(user_id, coin, STRATEGY, token, mode)
    print(f"💼 Allocated USD for strategy: ${allocated_usd:.2f}")

    if allocated_usd <= 0:
        print(f"⚠️ No allocation set for {bot_name}. Setting state to Inactive.")
        state = {
            "status": "Inactive",
            "amount": 0.0,
            "buy_price": 0.0,
            "usd_held": 0.0
        }
        save_coin_state(user_id, coin, state, token, mode)
        return

    # === Initialize if state is empty
    if not state:
        print("🧾 No existing state. Checking live/paper balances...")
        balances = get_live_balances(user_id) if mode == "live" else load_portfolio_balances(user_id, token, mode)
        held = balances.get(coin.upper(), 0)
        print(f"📊 Held {coin.upper()} in account: {held:.6f}")

        if held > 0 and cur_price > 0:
            print(f"🔄 Initializing {bot_name} as Holding.")
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
                notes="Assigned BTC to RSI_5MIN strategy (virtual entry)"
            )
        else:
            state = {
                "status": "none",
                "amount": 0.0,
                "buy_price": 0.0
            }

    # === Buy Logic
    if state["status"] == "none" and rsi_value < 30:
        print("💡 Buy signal triggered (RSI < 30)")
        coin_amount = calculate_btc_allocation(cur_price, allocated_usd)
        print(f"🛒 Buying {coin_amount:.6f} {coin} at ${cur_price:.2f}")
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
                notes="RSI < 30 triggered entry"
            )

            state.update({
                "status": "Holding",
                "amount": coin_amount,
                "buy_price": cur_price
            })

    # === Sell Logic
    elif state["status"] == "Holding" and rsi_value > 70:
        print("💡 Sell signal triggered (RSI > 70)")
        coin_amount = state.get("amount", 0.0)
        buy_price = state.get("buy_price", 0.0)
        only_sell_profit = get_setting("only_sell_in_profit", STRATEGY.lower())
        profit_usd = (cur_price - buy_price) * coin_amount
        is_profitable = profit_usd > 1.00

        print(f"📈 Holding {coin_amount:.6f} {coin}, P/L = ${profit_usd:.2f} (Only sell in profit: {only_sell_profit})")

        if coin_amount > 0 and (not only_sell_profit or is_profitable):
            print(f"💵 Selling {coin_amount:.6f} {coin} at ${cur_price:.2f}")
            execute_trade(bot_name, "sell", coin_amount, cur_price, mode, coin)
            update_profit_json(user_id, coin, mode, coin_amount, profit_usd, token)

            log_trade_multi(
                coin=coin,
                strategy=STRATEGY,
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
            print(f"✅ Sold {coin_amount:.6f} {coin} — Profit: ${profit_usd:.2f}")
        else:
            print(f"⚠️ Sell skipped — Profit condition not met. P/L: ${profit_usd:.2f}")

    # === Save State
    save_coin_state(user_id, coin, state, token, mode)
    print(f"💾 State saved for {bot_name}: {state}")
