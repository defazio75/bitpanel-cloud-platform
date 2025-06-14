# bot_runner.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import traceback
import controller
    
if __name__ == "__main__":
    print("🚀 Starting BitPanel controller...")
    try:
        controller.run_controller()
    except Exception as e:
        print(f"❌ Fatal error in controller: {e}")
        traceback.print_exc()
