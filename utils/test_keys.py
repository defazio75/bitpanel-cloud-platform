import json
from utils.firebase_auth import sign_in
from utils.firebase_db import (
    load_portfolio_snapshot,
    save_portfolio_snapshot,
)
from utils.kraken_wrapper import get_live_balances
from utils.config import get_mode
from utils.load_keys import load_user_api_keys

# === USER CONFIG ===
email = "dave.defazio@gmail.com"   # ✅ Replace with your Firebase email
password = "Allfor1!"       # ✅ Replace with your Firebase password
exchange = "kraken"

# === LOGIN & AUTH ===
auth_user = sign_in(email, password)
user_id = auth_user["localId"]
token = auth_user["idToken"]
mode = "live"  # specifically test live mode

print(f"🧪 Running Live Mode Test for: {user_id}")

# === 1. Load API Keys ===
print("\n🔑 Decrypting Kraken Keys...")
keys = load_user_api_keys(user_id, exchange, token=token)
print("✅ Key:", keys['key'][:6] + "...")
print("✅ Secret:", keys['secret'][:6] + "...")

# === 2. Pull Live Balances ===
print("\n📡 Fetching Live Kraken Balances...")
balances = get_live_balances(user_id=user_id)
print("✅ Live Balances from Kraken:\n", json.dumps(balances, indent=2))

# === 3. Save to Firebase ===
print("\n💾 Saving Live Snapshot to Firebase...")
save_path = "portfolio/portfolio_snapshot.json"
save_portfolio_snapshot(user_id, save_path, balances, mode, token=token)

# === 4. Reload from Firebase ===
print("\n🔄 Reloading Snapshot from Firebase...")
reloaded = load_portfolio_snapshot(user_id, save_path, mode, token=token)
print("✅ Reloaded Firebase Snapshot:\n", json.dumps(reloaded, indent=2))
