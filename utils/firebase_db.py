import os
from datetime import datetime
import pytz
from utils.encryption import encrypt_string, decrypt_string
from utils.firebase_config import firebase
from utils.kraken_wrapper import get_live_balances, get_prices
from firebase_admin import db
from utils.firebase_config import db

FIREBASE_BASE_URL = "https://bitpanel-967b1-default-rtdb.firebaseio.com"

def get_all_user_ids():
    try:
        users_snapshot = db.child("users").get()
        if users_snapshot.each():
            return [user.key() for user in users_snapshot.each()]
        else:
            return []
    except Exception as e:
        print(f"❌ Error fetching user IDs: {e}")
        return []

# === USER PROFILE ===
def save_user_profile(user_id, email, name="New User"):
    """Save minimal user profile in Firebase under /users/{user_id}/profile/"""
    now = datetime.utcnow()
    profile_data = {
        "name": name,
        "email": email,
        "signup_date": now.strftime("%Y-%m-%d"),
        "account": {
            "role": "lead",
            "paid": False,
            "plan": None,
            "last_login": now.isoformat(),
            "last_payment_date": None
        }
    }

    try:
        firebase.database().child("users").child(user_id).child("profile").child("account").set(user_profile_dict, token)
        print(f"✅ User profile created for {user_id}")
    except Exception as e:
        print(f"❌ Failed to save profile for {user_id}: {e}")

def update_last_login(user_id, token):
    tz = pytz.timezone("America/Chicago")
    last_login = datetime.now(tz).strftime("%B %-d, %Y at %-I:%M %p %Z")
    firebase.database().child("users").child(user_id).child("profile").update({
        "last_login": last_login
    }, token)

def get_user_profile(user_id, token=None):
    try:
        result = firebase.database().child("users").child(user_id).child("profile").child("account").get(token)
        return result.val() if result.val() else {}
    except Exception as e:
        print(f"❌ Error fetching profile for {user_id}: {e}")
        return {}

# === API KEYS ===
def save_user_api_keys(user_id, exchange, api_key, api_secret, token):
    encrypted_key = encrypt_string(api_key, user_id)
    encrypted_secret = encrypt_string(api_secret, user_id)
    firebase.database().child("users").child(user_id).child("api_keys").child(exchange).set({
        "public": encrypted_key,
        "private": encrypted_secret
    }, token)

# === STRATEGY CONFIGURATION ===
def save_strategy_allocations(user_id, coin, config, mode, token):
    firebase.database() \
        .child("users") \
        .child(user_id) \
        .child(mode) \
        .child("strategy_allocations") \
        .child(coin) \
        .set(config, token)

# === Get Strategy USD Allocation from Percent in Firebase ===
def load_strategy_allocation(user_id, coin, strategy_key, token, mode):
    # Load saved percentage allocations
    data = load_strategy_allocations(user_id, token, mode) or {}
    allocation_pct = data.get(coin.upper(), {}).get(strategy_key, 0.0)

    # Load portfolio snapshot for total value
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    usd_balance = snapshot.get("usd_balance", 0.0)
    total_value = usd_balance
    for info in snapshot.get("coins", {}).values():
        total_value += info.get("usd", 0.0)

    allocated_usd = (allocation_pct / 100.0) * total_value
    return round(allocated_usd, 2)

# === PORTFOLIO SNAPSHOT ===
def save_portfolio_snapshot(user_id, snapshot, token=None, mode="paper"):
    path = f"users/{user_id}/{mode}/balances/portfolio_snapshot"
    print(f"📤 Saving snapshot to {path}")
    firebase.database().child(path).set(snapshot, token)

def save_portfolio_history_snapshot(user_id, snapshot, token=None, mode="paper"):
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    path = f"users/{user_id}/{mode}/balances/history/{date_str}"
    print(f"🗂️ Saving daily history snapshot to {path}")
    firebase.database().child(path).set(snapshot, token)

# === Get Coin Balances from Portfolio Snapshot ===
def load_portfolio_balances(user_id, token, mode):
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    balances = {}
    if snapshot and "coins" in snapshot:
        for coin, info in snapshot["coins"].items():
            balances[coin.upper()] = info.get("balance", 0.0)
    balances["USD"] = snapshot.get("usd_balance", 0.0)
    return balances

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

def save_live_snapshot_from_kraken(user_id, token, mode="live", debug=False):
    if debug:
        st.write(f"🟢 [DEBUG] Starting live snapshot save for user `{user_id}` in `{mode}` mode...")

    balances = get_live_balances(user_id=user_id, token=token)
    prices = get_prices(user_id=user_id)

    if debug:
        st.write("✅ [DEBUG] Raw balances returned:", balances)
        st.write("📈 [DEBUG] Current prices:", prices)

    if not balances:
        if debug:
            st.error("❌ No balances returned from Kraken.")
        return

    tracked_symbols = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]
    coins = {}

    usd_balance = float(balances.get("USD", 0.0))
    total_value = usd_balance

    for symbol in tracked_symbols:
        raw_amt = balances.get(symbol, 0.0)
        price = prices.get(symbol, 0.0)

        if raw_amt is None:
            if debug:
                st.warning(f"⚠️ [{symbol}] balance was None — defaulted to 0")
            raw_amt = 0.0

        try:
            amount = float(raw_amt)
        except Exception as e:
            amount = 0.0
            if debug:
                st.error(f"❌ Failed to parse amount for {symbol}: {e}")

        usd_value = round(amount * price, 2)
        coins[symbol] = {
            "balance": round(amount, 8),
            "usd_value": usd_value
        }
        total_value += usd_value

        if debug:
            st.write(f"🔍 {symbol}: {amount} × ${price} = ${usd_value}")

    snapshot = {
        "usd_balance": round(usd_balance, 2),
        "coins": coins,
        "timestamp": datetime.utcnow().isoformat(),
        "total_value": round(total_value, 2)
    }

    if debug:
        st.write("📦 [DEBUG] Final snapshot payload:", snapshot)

    try:
        firebase.database() \
            .child("users") \
            .child(user_id) \
            .child(mode) \
            .child("balances") \
            .child("portfolio_snapshot") \
            .set(snapshot, token)

        if debug:
            st.success("✅ Snapshot successfully written to Firebase.")
    except Exception as e:
        if debug:
            st.error("❌ Failed to write snapshot to Firebase.")
            st.exception(e)

def initialize_strategy_state(user_id, coin, strategy, mode="paper", token=None, amount=None):
    from utils.kraken_wrapper import get_prices
    prices = get_prices(user_id=user_id)
    price = prices.get(coin.upper(), 0.0)

    # Load current coin state
    state = load_coin_state(user_id=user_id, coin=coin, token=token, mode=mode)

    # Default logic for backward compatibility if amount is not passed
    if amount is None:
        snapshot = load_portfolio_snapshot(user_id, token, mode)
        coin_balance = snapshot.get("coins", {}).get(coin.upper(), {}).get("balance", 0.0)

        existing_active = sum(1 for s in state if state[s].get("status") == "Active")
        if strategy not in state:
            existing_active += 1
        active_count = existing_active if existing_active > 0 else 1
        amount = round(coin_balance / active_count, 8)

    state[strategy] = {
        "status": "Active",
        "amount": amount,
        "usd_held": 0.0,
        "buy_price": price,
        "indicator": "—",
        "target": get_default_target(strategy),
        "last_action": "Waiting",
        "timestamp": datetime.utcnow().isoformat()
    }

    save_coin_state(user_id=user_id, coin=coin, state_data=state, token=token, mode=mode)

def get_default_target(strategy):
    return {
        "RSI_5MIN": "RSI < 30",
        "RSI_1HR": "RSI < 30 / > 70",
        "BOLLINGER": "Bandwidth breakout",
        "HODL": "Hold position"
    }.get(strategy.upper(), "—")
