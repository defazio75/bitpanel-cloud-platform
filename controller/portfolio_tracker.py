import os
import sys
import json
from config.mode_loader import get_mode

# Set project root dynamically
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

PAPER_PORTFOLIO_PATH = os.path.join(PROJECT_ROOT, "logs", "paper", "paper_portfolio.json")
LIVE_PORTFOLIO_PATH = os.path.join(PROJECT_ROOT, "logs", "live", "live_portfolio.json")

def get_portfolio_snapshot():
    mode = get_mode()
    if mode == "paper":
        return load_paper_balances()
    elif mode == "live":
        return load_live_balances()

def load_paper_balances():
    if not os.path.exists(PAPER_PORTFOLIO_PATH):
        print("⚠️ No paper portfolio file found!")
        return {}
    with open(PAPER_PORTFOLIO_PATH, 'r') as f:
        return json.load(f)

def load_live_balances():
    if not os.path.exists(LIVE_PORTFOLIO_PATH):
        print("⚠️ No live portfolio file found!")
        return {}
    with open(LIVE_PORTFOLIO_PATH, 'r') as f:
        return json.load(f)