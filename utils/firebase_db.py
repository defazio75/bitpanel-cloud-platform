import streamlit as st
from datetime import datetime
import pytz
from utils.encryption import encrypt_string, decrypt_string
from utils.firebase_config import firebase

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

def save_live_snapshot_and_state(user_id, token, balances, prices, mode="live"):
    from datetime import datetime

    usd_balance = float(balances.get("USD", 0.0))
    coins = {}
    total_value = usd_balance

    for coin, amount in balances.items():
        if coin == "USD" or amount == 0:
            continue

        price = prices.get(coin, 0.0)
        usd_value = round(amount * price, 2)

        # === Save to coins block ===
        coins[coin] = {
            "balance": round(amount, 6),
            "value": usd_value
        }

        total_value += usd_value

        # === Save HODL Strategy State ===
        coin_state = {
            "HODL": {
                "amount": round(amount, 6),
                "buy_price": round(price, 2),
                "status": "Active",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        save_coin_state(user_id=user_id, coin=coin, state_data=coin_state, token=token, mode=mode)

    snapshot = {
        "usd_balance": round(usd_balance, 2),
        "coins": coins,
        "total_value": round(total_value, 2),
        "timestamp": datetime.utcnow().isoformat()
    }

    save_portfolio_snapshot(user_id=user_id, snapshot=snapshot, token=token, mode=mode)

    except Exception as e:
        print(f"❌ Failed to list files at {path}: {e}")
        return []
