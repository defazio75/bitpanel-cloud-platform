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

from utils.firebase_db import get_all_user_ids, get_user_profile, save_portfolio_snapshot
print("✅ firebase_db methods imported")

from bots import rsi_5min, rsi_1hr, bollinger, dca_matrix
print("✅ bots imported")

from utils.portfolio_writer import write_portfolio_snapshot
print("✅ portfolio_writer imported")

print("🎯 All controller.py imports successful")

LOOP_INTERVAL = 60  # Run every 60 seconds

# === Main Controller ===
def run_controller():
    print("🧠 STEP 3: Entered run_controller()")

    try:
        user_ids = get_all_user_ids()
        print(f"🔍 STEP 4: Retrieved user IDs: {user_ids}")
    except Exception as e:
        print(f"❌ STEP 4: Failed to get user IDs: {e}")
        traceback.print_exc()
        return

    for user_id in user_ids:
        print(f"👤 STEP 5: Starting setup for user {user_id}")

        try:
            profile = get_user_profile(user_id, token=None)
            exchange_name = profile.get("exchange", "kraken")
            print(f"🔁 STEP 6: Exchange for {user_id}: {exchange_name}")

            # Write both paper and live snapshots to Firebase
            write_portfolio_snapshot(user_id=user_id, mode="paper", token=None)
            write_portfolio_snapshot(user_id=user_id, mode="live", token=None)
            print(f"📝 STEP 7: Snapshots (paper + live) saved for {user_id}")

            # === Run RSI 5-Min Bot (Safe Isolation) ===
            try:
                print(f"⚙️ STEP 8: Launching RSI 5-Min Bot for {user_id}")
                rsi_5min.run(user_id=user_id, token=None)
                print(f"✅ RSI 5-Min Bot completed for {user_id}")
            except Exception as bot_err:
                print(f"❌ RSI 5-Min Bot failed for {user_id}: {bot_err}")
                traceback.print_exc()

        except Exception as e:
            print(f"❌ Error during setup for {user_id}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    while True:
        run_controller()
        time.sleep(LOOP_INTERVAL)
