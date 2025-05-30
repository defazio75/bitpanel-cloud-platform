import time
import traceback
from utils.firebase_db import get_all_user_ids, get_api_keys, load_strategy_config
from utils.exchange_manager import get_exchange
from bots import rsi_5min, rsi_1hr, bollinger, dca_matrix
from config.config import get_mode

LOOP_INTERVAL = 60  # Run every 60 seconds

def run_controller():
    while True:
        print(f"🔁 Running controller loop at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        user_ids = get_all_user_ids()

        for user_id in user_ids:
            try:
                mode = get_mode(user_id)
                strategy_config = load_strategy_config(user_id, token=None)  # Public read allowed in paper

                if mode == "live":
                    api_keys = get_api_keys(user_id)
                    if not api_keys:
                        print(f"⚠️ Skipping {user_id} (no API keys in live mode)")
                        continue
                    token = api_keys.get("token")
                    exchange = get_exchange("kraken", mode="live", api_keys=api_keys)
                else:
                    token = None
                    exchange = get_exchange("kraken", mode="paper", api_keys=None)

                # === Strategy Bot Triggers ===
                if strategy_config.get("BTC", {}).get("rsi_5min", {}).get("enabled"):
                    rsi_5min.run(user_id, exchange, strategy_config)

                if strategy_config.get("BTC", {}).get("rsi_1hr", {}).get("enabled"):
                    rsi_1hr.run(user_id, exchange, strategy_config)

                if strategy_config.get("BTC", {}).get("bollinger", {}).get("enabled"):
                    bollinger.run(user_id, exchange, strategy_config)

                if strategy_config.get("BTC", {}).get("dca_matrix", {}).get("enabled"):
                    dca_matrix.run(user_id, exchange, strategy_config)

            except Exception as e:
                print(f"❌ Error running bots for user {user_id}: {e}")
                traceback.print_exc()

        print("⏳ Waiting for next loop...\n")
        time.sleep(LOOP_INTERVAL)

if __name__ == "__main__":
    run_controller()
