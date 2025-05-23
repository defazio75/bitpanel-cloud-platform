# === Strategy Configuration ===

# Allocation settings
BTC_HOLDING_PERCENT = 0.25
RSI_5MIN_ALLOC_PERCENT = 0.25
RSI_1HR_ALLOC_PERCENT = 0.25
BOLLINGER_ALLOC_PERCENT = 0.25

# RSI Strategy
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_5MIN_PROFIT_TARGET = 0.02
RSI_1HR_PROFIT_TARGET = 0.03

# Bollinger Band Strategy
BOLLINGER_WINDOW = 20
BOLLINGER_DEV = 2
BOLLINGER_PROFIT_TRIGGER = 0.02
BOLLINGER_TRAIL_DROP = 0.01

# Market settings
BASE_PAIR = 'XXBTZUSD'
QUOTE_ASSET = 'ZUSD'

# General
MIN_TRADE_USD = 10

def get_mode():
    try:
        with open("config/mode.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "paper"
