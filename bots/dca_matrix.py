from datetime import datetime
from utils.config import get_mode
from utils.kraken_wrapper import get_live_balances, get_live_prices
from utils.paper_reset import load_paper_balances
from utils.trade_executor import execute_trade
from utils.performance_logger import log_dca_trade
from utils.firebase_db import load_firebase_json, save_firebase_json
import streamlit as st

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

def load_strategy_usd(user_id, coin, strategy_key, mode, token):
    path = f"{mode}/allocations/strategy_allocations.json"
    data = load_firebase_json(path, user_id, token) or {}
    return data.get(coin.upper(), {}).get(strategy_key.upper(), 0.0)

# === Main Bot Logic ===
def run(price_data, user_id, coin="BTC", mode=None):
    if not mode:
        mode = get_mode()
    print(f"\n🔁 Running {STRATEGY} for {user_id} in {mode.upper()} mode")

    token = st.session_state.user["token"]
    cur_price = price_data.get("price")
    bot_name = STRATEGY.lower()
    state_path = f"{mode}/current/{coin}/{STRATEGY}.json"
    state = load_firebase_json(state_path, user_id, token) or {}

    allocated_usd = load_strategy_usd(user_id, coin, STRATEGY, mode, token)
    if allocated_usd <= 0:
        print(f"⚠️ No USD allocation set for {STRATEGY}. Exiting.")
        return

    # Init state
    last_high = state.get("last_high", cur_price)
    if cur_price > last_high:
        last_high = cur_price

    open_tranches = state.get("open_tranches", [])
    sold_tranches = state.get("sold_tranches", [])
    balances = get_live_balances(user_id) if mode == "live" else load_paper_balances(user_id)

    # === Auto-initialize if BTC is held but state is empty
    if not open_tranches and balances.get(coin.upper(), 0) > 0:
        amount = balances[coin.upper()]
        usd_spent = amount * cur_price
        open_tranches.append({
            "zone": 0,
            "drop_pct": 0,
            "buy_price": cur_price,
            "sell_pct": DCA_ZONES[0]["sell_pct"],
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
            usd_to_use = allocated_usd * (zone["alloc_pct"] / 100)
            amount = usd_to_use / cur_price
            execute_trade(bot_name, "buy", amount, cur_price, mode, coin)

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
            execute_trade(bot_name, "sell", t["amount"], cur_price, mode, coin)

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
                "profit_usd": round(profit_usd, 2),
                "timestamp": datetime.utcnow().isoformat()
            })

            print(f"💰 Sold zone {t['zone']} @ ${cur_price:,.2f}, profit = ${profit_usd:.2f}")
        else:
            new_tranches.append(t)

    # === Save Updated State ===
    state = {
        "last_high": last_high,
        "open_tranches": new_tranches,
        "sold_tranches": sold_tranches
    }
    save_firebase_json(state_path, state, user_id, token)
    print(f"💾 {STRATEGY} state saved")
