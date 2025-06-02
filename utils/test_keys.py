import json
from utils.firebase_db import (
    load_portfolio_snapshot_from_firebase,
    load_user_data
)
from utils.kraken_wrapper import get_live_balances
from utils.config import get_mode
from utils.load_keys import load_user_api_keys

user_id = "YOUR_TEST_USER_ID"  # ← replace this with your Firebase UID
exchange = "kraken"
mode = get_mode(user_id)

print("🔐 Testing Firebase + Kraken Decryption + Live Pull")

# === Test API Key Decryption ===
print("\n🔑 Testing API Key Decryption...")
keys = load_user_api_keys(user_id, exchange)
if keys:
    print("✅ Decrypted API Key:", keys["key"][:8] + "...")
    print("✅ Decrypted API Secret:", keys["secret"][:8] + "...")
else:
    print("❌ Failed to load API keys")

# === Test Live Kraken Balance ===
print("\n💰 Testing Live Kraken Balance Fetch...")
try:
    balances = get_live_balances(user_id=user_id)
    print("✅ Live Balances:", json.dumps(balances, indent=2))
except Exception as e:
    print("❌ Error getting balances:", e)

# === Test Firebase Portfolio Snapshot ===
print("\n📊 Testing Firebase Portfolio Snapshot...")
try:
    token = None
    snapshot = load_portfolio_snapshot_from_firebase(user_id, token, mode)
    print("✅ Firebase Snapshot:", json.dumps(snapshot, indent=2))
except Exception as e:
    print("❌ Error loading snapshot:", e)

# === Test Firebase Bot State (e.g. BTC) ===
print("\n📁 Testing Firebase Bot State (BTC_state)...")
try:
    btc_state = load_user_data(user_id, "current/BTC_state.json", mode)
    print("✅ BTC Bot State:", json.dumps(btc_state, indent=2))
except Exception as e:
    print("❌ Error loading BTC state:", e)
