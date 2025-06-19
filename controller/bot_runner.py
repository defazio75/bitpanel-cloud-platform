# bot_runner.py
print("🧪 Step 1: Top of bot_runner")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("🧪 Step 2: Path appended")

import time
import traceback
print("🧪 Step 3: Time and traceback imported")

try:
    import controller
    print("✅ Step 4: Controller imported successfully")
except Exception as e:
    print(f"❌ Step 4: Failed to import controller: {e}")
    traceback.print_exc()

print("✅ Step 5: Hello from bot_runner")

if __name__ == "__main__":
    print("🚀 Step 6: Starting BitPanel controller...")
    try:
        controller.run_controller()
    except Exception as e:
        print(f"❌ Step 7: Fatal error in controller: {e}")
        traceback.print_exc()
