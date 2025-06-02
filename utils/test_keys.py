from utils.firebase_db import load_user_api_keys
from utils.encryption import decrypt_string
import streamlit as st

# Set your test user ID here
user_id = "YOUR_USER_ID"
exchange = "kraken"

try:
    print("📡 Loading encrypted API keys from Firebase...")
    keys = load_user_api_keys(user_id, exchange)
    print("🔑 Loaded Keys:", keys)

    print("✅ Key:", keys.get("key")[:6], "...")
    print("✅ Secret:", keys.get("secret")[:6], "...")

except Exception as e:
    print("❌ ERROR:", e)
