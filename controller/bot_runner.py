# bot_runner.py
import time
import traceback
from bots import rsi_5min, rsi_1hr, bollinger, dca_matrix

def run_all_bots():
    print("🚀 Running all strategy bots...")
    rsi_5min.run()
    rsi_1hr.run()
    bollinger.run()
    dca_matrix.run()
    print("✅ All bots executed.\n")
    
if __name__ == "__main__":
    while True:
        run_all_bots()
        time.sleep(60)
