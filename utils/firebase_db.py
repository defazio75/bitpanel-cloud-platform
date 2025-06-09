import streamlit as st
from datetime import datetime
import pytz
from utils.encryption import encrypt_string, decrypt_string
from utils.firebase_config import firebase
from utils.kraken_wrapper import get_live_balances, get_prices

FIREBASE_BASE_URL = "https://bitpanel-967b1-default-rtdb.firebaseio.com"

# === USER PROFILE ===
def save_user_profile(user_id, name, email, signup_date=None, last_login=None):
    tz = pytz.timezone("America/Chicago")
    if not signup_date:
        signup_date = datetime.now(tz).strftime("%B %-d, %Y at %-I:%M %p %Z")
    if not last_login:
        last_login = datetime.now(tz).strftime("%B %-d, %Y at %-I:%M %p %Z")
    profile_data = {
        "name": name,
        "email": email,
        "signup_date": signup_date,
        "last_login": last_login
    }
    firebase.database().child("users").child(user_id).child("profile").set(profile_data)

def update_last_login(user_id, token):
    tz = pytz.timezone("America/Chicago")
    last_login = datetime.now(tz).strftime("%B %-d, %Y at %-I:%M %p %Z")
    firebase.database().child("users").child(user_id).child("profile").update({
        "last_login": last_login
    }, token)

def load_user_profile(user_id, token):
    result = firebase.database().child("users").child(user_id).child("profile").get(token)
    return result.val() if result.val() else None

# === API KEYS ===
def save_user_api_keys(user_id, exchange, api_key, api_secret, token):
    encrypted_key = encrypt_string(api_key, user_id)
    encrypted_secret = encrypt_string(api_secret, user_id)
    firebase.database().child("users").child(user_id).child("api_keys").child(exchange).set({
        "public": encrypted_key,
        "private": encrypted_secret
    }, token)

# === STRATEGY CONFIGURATION ===
def save_strategy_allocations(user_id, config, token, mode):
    firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("strategy_allocations") \
        .set(config, token)

def load_strategy_allocations(user_id, token, mode):
    data = firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("strategy_allocations") \
        .get(token) \
        .val()

# === PORTFOLIO SNAPSHOT ===
def save_portfolio_snapshot(user_id, snapshot, token, mode):
    firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("balances") \
        .child("portfolio_snapshot") \
        .set(snapshot, token)

def load_portfolio_snapshot(user_id, token, mode):
    data = firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("balances") \
        .child("portfolio_snapshot") \
        .get(token) \
        .val()
    return data if data else {}

# === COIN STATE ===
def save_coin_state(user_id, coin, state_data, token, mode):
    firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("current") \
        .child(f"{coin}_state") \
        .set(state_data, token)

def load_coin_state(user_id, coin, token, mode):
    data = firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("current") \
        .child(f"{coin}_state") \
        .get(token) \
        .val()
    return data if data else {}

# === PERFORMANCE HISTORY ===
def save_performance_snapshot(user_id, snapshot, date_str, token, mode):
    firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("history") \
        .child(date_str) \
        .set(snapshot, token)

def load_performance_snapshot(user_id, token, mode):
    data = firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("history") \
        .get(token) \
        .val()
    return data if data else {}

def create_default_snapshot(user_id, token, mode, usd_balance=100000.0):
    coins = {
        coin: {
            "balance": 0.0,
        }
        for coin in SUPPORTED_COINS
    }

    snapshot = {
        "usd_balance": usd_balance,
        "coins": coins,
        "timestamp": datetime.utcnow().isoformat(),
        "total_value": usd_balance
    }

    save_portfolio_snapshot(user_id=user_id, snapshot=snapshot, token=token, mode=mode)
    print(f"✅ Initialized {mode} account for {user_id} with ${usd_balance:.2f} USD and 0.0 in all coins.")

# === FILE LISTING ===
def list_firebase_files(path, mode, user_id):
    token = st.session_state.user.get("token")
    try:
        data = firebase.database().child("users").child(user_id).child(mode).child(path).get(token)
        if data.each():
            return [item.key() for item in data.each()]
        return []
    except Exception as e:
        print(f"❌ Failed to list files at {path}: {e}")
        return []

def save_live_snapshot_from_kraken(user_id, token, mode="live"):
    """Pull live balances from Kraken and save as a portfolio snapshot in Firebase."""
    print(f"[DEBUG] Pulling balances from Kraken for {user_id} in {mode} mode...")
    balances = get_live_balances(user_id=user_id, token=token)
    prices = get_prices(user_id=user_id)

    if not balances:
        print("❌ No balances returned from Kraken.")
        return

    usd_balance = float(balances.get("USD", 0.0))
    total_value = usd_balance
    coins = {}

    for coin in ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]:
        raw_amount = balances.get(coin, 0.0)
        try:
            amount = float(raw_amount)
        except Exception:
            amount = 0.0

        usd_value = round(amount * prices.get(coin, 0.0), 2)
        coins[coin] = {
            "balance": round(amount, 8),
            "usd_value": usd_value
        }
        total_value += usd_value

    snapshot = {
        "usd_balance": round(usd_balance, 2),
        "coins": coins,
        "timestamp": datetime.utcnow().isoformat(),
        "total_value": round(total_value, 2)
    }

    print("[DEBUG] Final Snapshot to be saved:", snapshot)

    firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("balances") \
        .child("portfolio_snapshot") \
        .set(snapshot, token)

    print(f"✅ Snapshot saved to Firebase for user {user_id} in {mode} mode.")


def load_latest_snapshot(user_id, token, mode="live"):
    """Retrieve the saved snapshot from Firebase for the dashboard display."""
    return load_portfolio_snapshot(user_id=user_id, token=token, mode=mode)

