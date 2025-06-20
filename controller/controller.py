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

from utils.firebase_db import get_all_user_ids, get_user_profile, load_strategy_allocations, save_portfolio_snapshot
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
        print(f"🧪 Starting snapshot thread for {user_id}")
        mode = get_mode(user_id)
        print(f"🔍 Snapshot mode for {user_id}: {mode}")
        
        while True:
            try:
                print(f"[SNAPSHOT] Attempting snapshot for {user_id} in {mode}")
                write_portfolio_snapshot(user_id=user_id, mode=mode, token=token)
                print(f"[SNAPSHOT] ✅ Snapshot complete for {user_id}")
            except Exception as e:
                print(f"❌ Error writing snapshot for {user_id}: {e}")
                traceback.print_exc()
            time.sleep(5)

    except Exception as e:
        print(f"❌ Snapshot thread crashed for {user_id}: {e}")
        traceback.print_exc()

# === Main Controller ===
def run_controller():
    print("🧠 STEP 3: Entered run_controller()")

    try:
        user_ids = get_all_user_ids()
        print(f"🔍 STEP 4: Retrieved user IDs: {user_ids}")
    except Exception as e:
        print(f"❌ STEP 4: Failed to get user IDs: {e}")
        import traceback; traceback.print_exc()
        return

    for user_id in user_ids:
        print(f"👤 STEP 5: Starting setup for user {user_id}")

        try:
            token = load_user_api_keys(user_id).get("token")  # or however you retrieve the token
            profile = get_user_profile(user_id, token)
            exchange_name = profile.get("exchange", "kraken")  # default to kraken if not set
            api_keys = profile.get("api_keys", {})
            mode = get_mode(user_id)
            
            exchange = get_exchange(exchange_name=exchange_name, mode=mode, api_keys=api_keys)
            print(f"🔁 STEP 6: Exchange loaded for {user_id}: {exchange.name}")

            strategy_config = load_strategy_allocations(user_id)
            print(f"🧠 STEP 7: Strategy config for {user_id}: {strategy_config}")

            # TEMP: Don't run any threads yet — just confirm logic flow
            print(f"✅ STEP 8: Ready to launch strategies for {user_id}... (skipped for now)")

        except Exception as e:
            print(f"❌ Error during setup for {user_id}: {e}")
            traceback.print_exc()
