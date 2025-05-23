import time
from exchanges.exchange_manager import get_exchange
from strategies.rsi_5min import run_strategy as rsi_5min_run
from strategies.rsi_1hr import run_strategy as rsi_1hr_run
from strategies.bollinger_breakout import run_strategy as bollinger_run
from strategies.dca_matrix import run as dca_matrix_run  # ✅ NEW
from dashboard.utils.allocation_manager import load_allocations
from dashboard.utils.state_loader import load_portfolio_summary
from utils.portfolio_writer import write_portfolio_snapshot  # ✅ ADD THIS

def main():
    print("\n🟢 BitPanel Core Engine Starting...\n")

    # === Load Mode and Setup Exchange ===
    from config.config import get_mode
    mode = get_mode()
    print(f"🚀 Running bots in {mode.upper()} MODE\n")
    exchange = get_exchange("kraken", mode=mode)

    # === Load Allocations and Portfolio ===
    allocations = load_allocations()
    portfolio = load_portfolio_summary()

    total_portfolio_value = portfolio.get('total', 0.0)
    btc_price = portfolio.get('btc_price', 0.0)

    # === Loop Through Coins and Assigned Strategies ===
    for coin, strategies in allocations.items():
        for strategy, alloc_pct in strategies.items():
            if alloc_pct > 0:
                allocated_usd = (alloc_pct / 100) * total_portfolio_value

                print(f"📈 {coin} | {strategy} | Allocated: ${allocated_usd:,.2f}")

                if strategy == "RSI 5-Min":
                    rsi_5min_run(exchange, coin, allocated_usd, mode=mode)
                elif strategy == "RSI 1-Hour":
                    rsi_1hr_run(exchange, coin, allocated_usd, mode=mode)
                elif strategy == "Bollinger":
                    bollinger_run(exchange, coin, allocated_usd, mode=mode)
                elif strategy == "DCA Matrix":  # ✅ NEW
                    dca_matrix_run({"price": btc_price}, coin=coin, mode=mode)

    # === Save Portfolio Snapshot ===
    usd_balance = exchange.get_usd_balance()
    coin_data = {}
    for coin in portfolio.get("coins", {}):  # ✅ SAFER ACCESS
        balance = exchange.get_balance(coin)
        price = exchange.get_price(coin)
        coin_data[coin] = {
            "balance": balance,
            "price": price,
            "value": balance * price
        }

    write_portfolio_snapshot(exchange.mode, usd_balance, coin_data)

    print("\n✅ BitPanel Core Engine Completed This Cycle.\n")

if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)