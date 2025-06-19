import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import threading
import traceback
from utils.firebase_db import get_all_user_ids, load_strategy_allocations, save_portfolio_snapshot
from exchange.exchange_manager import get_exchange
from bots import rsi_5min, rsi_1hr, bollinger, dca_matrix
from utils.config import get_mode
from utils.load_keys import load_user_api_keys
from utils.portfolio_writer import write_portfolio_snapshot

LOOP_INTERVAL = 60  # Run every 60 seconds

# === Background Snapshot Thread ===
def snapshot_loop(user_id, token):
    mode = get_mode(user_id)
    while True:
        print(f"[SNAPSHOT] Saving snapshot for {user_id} in {mode} mode...")
        write_portfolio_snapshot(user_id=user_id, mode=mode, token=token)
        time.sleep(60)

# === Main Controller ===
def run_controller():
    user_ids = get_all_user_ids()

    # Launch snapshot thread once per user
    for user_id in user_ids:
        try:
            mode = get_mode(user_id)
            token = None
            if mode == "live":
                api_keys = load_user_api_keys(user_id, token=token)
                token = api_keys.get("token") if api_keys else None
            else:
                token = None

            threading.Thread(target=snapshot_loop, args=(user_id, token), daemon=True).start()

        except Exception as e:
            print(f"❌ Error starting snapshot thread for {user_id}: {e}")
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
