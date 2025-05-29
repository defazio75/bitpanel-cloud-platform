import os
import json
from datetime import datetime
from config.config import get_mode
from utils.trade_executor import execute_trade
from utils.account_summary import get_total_portfolio_value
from utils.state_loader import load_strategy_allocations
from utils.kraken_wrapper import get_live_balances, get_live_prices
from utils.paper_reset import load_paper_balances
from utils.performance_logger import log_dca_trade

STRATEGY = "DCA_MATRIX"

# === DCA Matrix Definition ===
DCA_ZONES = [
    {"drop_pct": 1, "alloc_pct": 2, "sell_pct": 1},
    {"drop_pct": 2, "alloc_pct": 4, "sell_pct": 1},
    {"drop_pct": 3, "alloc_pct": 8, "sell_pct": 2},
    {"drop_pct": 5, "alloc_pct": 16, "sell_pct": 2},
    {"drop_pct": 7, "alloc_pct": 30, "sell_pct": 3},
    {"drop_pct": 10, "alloc_pct": 40, "sell_pct": 3}
]
def load_strategy_allocation(user_id, coin, strategy_name, mode):
    path = f"data/json_{mode}/{user_id}/current/{coin}_state.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return data.get(strategy_name, {}).get("allocation_pct", 0)
    return 0

# === Load state ===
def load_bot_state(user_id, coin, mode):
    path = f"data/json_{mode}/{user_id}/current/{coin}_state.json"
    try:
        with open(path, "r") as f:
            return json.load(f).get(STRATEGY, {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# === Save state ===
def save_bot_state(user_id, coin, mode, state):
    path = f"data/json_{mode}/{user_id}/current/{coin}_state.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    full = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            full = json.load(f)
    full[STRATEGY] = state
    with open(path, "w") as f:
        json.dump(full, f, indent=2)

# === Main Bot Logic ===
def run(price_data, user_id, coin="BTC", mode=None):
    if not mode:
        mode = get_mode()
    print(f"\n🔁 Running {STRATEGY} for {user_id} in {mode.upper()} mode")

    state = load_bot_state(user_id, coin, mode)
    cur_price = price_data.get("price")
    allocation_pct = load_strategy_allocation(user_id, coin, STRATEGY, mode)

    if allocation_pct <= 0:
        print(f"⚠️ No allocation set for {STRATEGY}. Exiting.")
        return

    # Init state
    last_high = state.get("last_high", cur_price)
    if cur_price > last_high:
        last_high = cur_price

    open_tranches = state.get("open_tranches", [])
    sold_tranches = state.get("sold_tranches", [])
    portfolio_value = get_total_portfolio_value(user_id, mode)
    balances = get_live_balances(user_id) if mode == "live" else load_paper_balances(user_id)

    # === Auto-initialize tranche if BTC is held but bot is empty ===
    if not open_tranches and balances.get(coin.upper(), 0) > 0:
        amount = balances[coin.upper()]
        usd_spent = amount * cur_price
        open_tranches.append({
            "zone": 0,
            "drop_pct": 0,
            "buy_price": cur_price,
            "sell_pct": DCA_ZONES[0]["sell_pct"],  # default to first zone's sell_pct
            "amount": amount,
            "usd_spent": usd_spent,
            "timestamp": datetime.utcnow().isoformat()
        })

        log_dca_trade(
            user_id=user_id,
            coin=coin,
            action="buy",
            amount=amount,
            price=cur_price,
            mode=mode,
            notes="Adopted initial BTC holdings into DCA Matrix"
        )

        print(f"📥 DCA Matrix auto-initialized with existing BTC: {amount:.6f} {coin} @ ${cur_price:,.2f}")

    # === BUY Logic ===
    bought_zones = [t["drop_pct"] for t in open_tranches]
    for i, zone in enumerate(DCA_ZONES):
        if zone["drop_pct"] in bought_zones:
            continue
        drop_trigger_price = last_high * (1 - zone["drop_pct"] / 100)
        if cur_price <= drop_trigger_price:
            usd_to_use = (allocation_pct / 100) * (zone["alloc_pct"] / 100) * portfolio_value
            amount = usd_to_use / cur_price
            execute_trade(STRATEGY.lower(), "buy", amount, cur_price, mode, coin)

            log_dca_trade(
                user_id=user_id,
                coin=coin,
                action="buy",
                amount=amount,
                price=cur_price,
                mode=mode,
                notes=f"DCA Matrix Zone {i+1} Entry"
            )

            open_tranches.append({
                "zone": i + 1,
                "drop_pct": zone["drop_pct"],
                "buy_price": cur_price,
                "sell_pct": zone["sell_pct"],
                "amount": amount,
                "usd_spent": usd_to_use,
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"✅ Bought zone {i+1}: {amount:.6f} {coin} @ ${cur_price:,.2f}")

    # === SELL Logic ===
    new_tranches = []
    for t in open_tranches:
        target = t["buy_price"] * (1 + t["sell_pct"] / 100)
        if cur_price >= target:
            execute_trade(STRATEGY.lower(), "sell", t["amount"], cur_price, mode, coin)

            log_dca_trade(
                user_id=user_id,
                coin=coin,
                action="sell",
                amount=t["amount"],
                price=cur_price,
                mode=mode,
                notes=f"DCA Matrix Zone {t['zone']} Exit"
            )

            profit_usd = (cur_price - t["buy_price"]) * t["amount"]
            sold_tranches.append({
                "zone": t["zone"],
                "buy_price": t["buy_price"],
                "sell_price": cur_price,
                "profit_btc": profit_btc,
                "timestamp": datetime.utcnow().isoformat()
            })
            print(f"💰 Sold zone {t['zone']} @ ${cur_price:,.2f}, profit = {profit_btc:.8f} BTC")
        else:
            new_tranches.append(t)

    state = {
        "last_high": last_high,
        "open_tranches": new_tranches,
        "sold_tranches": sold_tranches
    }
    save_bot_state(user_id, coin, mode, state)
    print(f"💾 {STRATEGY} state saved")

# if __name__ == "__main__":
#     run({"price": 98000}, user_id="test_user", coin="BTC", mode="paper")
