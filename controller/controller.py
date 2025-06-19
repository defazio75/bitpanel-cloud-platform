print("📦 Starting controller.py")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("✅ sys.path set")

import time
print("✅ time imported")

import threading
print("✅ threading imported")

import traceback
print("✅ traceback imported")

from utils.firebase_db import get_all_user_ids, load_strategy_allocations, save_portfolio_snapshot
print("✅ firebase_db methods imported")

from exchange.exchange_manager import get_exchange
print("✅ exchange manager imported")

from bots import rsi_5min, rsi_1hr, bollinger, dca_matrix
print("✅ bots imported")

from utils.config import get_mode
print("✅ config imported")

from utils.load_keys import load_user_api_keys
print("✅ load_keys imported")

from utils.portfolio_writer import write_portfolio_snapshot
print("✅ portfolio_writer imported")

print("🎯 All controller.py imports successful")

LOOP_INTERVAL = 60  # Run every 60 seconds

# === Background Snapshot Thread ===
def snapshot_loop(user_id, token):
    try:
        mode = get_mode(user_id)
        while True:
            try:
                print(f"[SNAPSHOT] Attempting snapshot for {user_id} in {mode}")
                write_portfolio_snapshot(user_id=user_id, mode=mode, token=token)
            except Exception as e:
                print(f"❌ Error writing snapshot for {user_id}: {e}")
                traceback.print_exc()
            time.sleep(60)
    except Exception as e:
        print(f"❌ Snapshot thread crashed for {user_id}: {e}")
        traceback.print_exc()

# === Main Controller ===
def run_controller():
    print("✅ Controller launched and loop is running")
    
    try:
        user_ids = get_all_user_ids()
        print(f"🧑‍💻 Loaded user_ids: {user_ids}")
    except Exception as e:
        print(f"❌ Failed to load user_ids: {e}")
        traceback.print_exc()
        return

    # Launch snapshot thread once per user
    for user_id in user_ids:
        try:
            mode = get_mode(user_id)
            print(f"🧾 Mode for {user_id}: {mode}")

            token = None
            if mode == "live":
                api_keys = load_user_api_keys(user_id, token=token)
                print(f"🔑 API keys for {user_id}: {api_keys}")
                token = api_keys.get("token") if api_keys else None

            threading.Thread(target=snapshot_loop, args=(user_id, token), daemon=True).start()

        except Exception as e:
            print(f"❌ Error during snapshot thread setup for {user_id}: {e}")
            traceback.print_exc()

    # Main loop runs bots
    while True:
        print(f"🔁 Running controller loop at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        for user_id in user_ids:
            try:
                mode = get_mode(user_id)

                if mode == "live":
                    api_keys = load_user_api_keys(user_id, token=token)
                    if not api_keys:
                        print(f"⚠️ Skipping {user_id} (no API keys in live mode)")
                        continue
                    token = api_keys.get("token")
                    user_exchange = api_keys.get("exchange", "kraken")
                    exchange = get_exchange(user_exchange, mode=mode, api_keys=api_keys)
                else:
                    token = None
                    exchange = get_exchange("kraken", mode=mode, api_keys=None)

                strategy_config = load_strategy_allocations(user_id, token=token, mode=mode)

                # === Strategy Bot Triggers ===
                try:
                    if strategy_config.get("BTC", {}).get("rsi_5min", {}).get("enabled"):
                        rsi_5min.run(user_id=user_id, token=token, coin="BTC")
                except Exception as e:
                    print(f"⚠️ RSI 5-Min bot failed for {user_id}: {e}")

                try:
                    if strategy_config.get("BTC", {}).get("rsi_1hr", {}).get("enabled"):
                        rsi_1hr.run(user_id, exchange, strategy_config)
                except Exception as e:
                    print(f"⚠️ RSI 1-Hour bot failed for {user_id}: {e}")
                    
                try:
                    if strategy_config.get("BTC", {}).get("bollinger", {}).get("enabled"):
                        bollinger.run(user_id, exchange, strategy_config)
                except Exception as e:
                    print(f"⚠️ Bollinger bot failed for {user_id}: {e}")

                try:
                    if strategy_config.get("BTC", {}).get("dca_matrix", {}).get("enabled"):
                        dca_matrix.run(user_id, exchange, strategy_config)
                except Exception as e:
                    print(f"⚠️ DCA Matrix bot failed for {user_id}: {e}")

            except Exception as e:
                print(f"❌ Error running bots for user {user_id}: {e}")
                traceback.print_exc()

        print("⏳ Waiting for next loop...\n")
        time.sleep(LOOP_INTERVAL)
