# bot_runner.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import traceback

print("✅ Hello from bot_runner")

try:
    import controller
    print("✅ controller.py imported successfully")
except Exception as e:
    print(f"❌ Failed to import controller: {e}")
    traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting BitPanel controller...")
    try:
        controller.run_controller()
    except Exception as e:
        print(f"❌ Fatal error in controller: {e}")
        traceback.print_exc()
