# bot_runner.py
import time
import traceback
from controller import run_all_bots  # Update if your function has a different name

if __name__ == "__main__":
    print("✅ BitPanel background bot runner started...")
    
    while True:
        try:
            run_all_bots()  # This should execute all your strategy logic
            print("✅ Bots executed successfully. Sleeping 60 seconds...")
        except Exception as e:
            print("❌ Error running bots:")
            traceback.print_exc()

        time.sleep(60)  # Wait 1 minute before the next execution
