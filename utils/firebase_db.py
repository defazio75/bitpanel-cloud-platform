import streamlit as st
import requests
from utils.encryption import encrypt_string, decrypt_string
from utils.firebase_config import firebase
import pyrebase

def save_user_profile(user_id, name, email, token, signup_date):
    db = firebase.database()
    db.child("users").child(user_id).set({
        "name": name,
        "email": email,
        "signup_date": signup_date
    }, token)

def update_last_login(user_id, token):
    db = firebase.database()
    db.child("users").child(user_id).update({
        "last_login": datetime.utcnow().isoformat() + "Z"
    }, token)

def load_user_profile(user_id, token):
    """
    Load user profile from Firebase Realtime Database using Pyrebase.
    """
    db = firebase.database()
    result = db.child("users").child(user_id).get(token)
    if result.val():
        return result.val()
    return None

def save_user_api_keys(user_id, exchange, api_key, api_secret):
    encrypted_key = encrypt_string(api_key, user_id)
    encrypted_secret = encrypt_string(api_secret, user_id)

    token = st.session_state.user["token"]
    db = firebase.database()
    db.child("users").child(user_id).child("api_keys").child(exchange).set({
        "key": encrypted_key,
        "secret": encrypted_secret
    }, token)

def load_user_api_keys(user_id, exchange):
    token = st.session_state.user["token"]
    db = firebase.database()
    result = db.child("users").child(user_id).child("api_keys").child(exchange).get(token)
    if result.val():
        encrypted_key = result.val().get("key", "")
        encrypted_secret = result.val().get("secret", "")
        return {
            "key": decrypt_string(encrypted_key, user_id),
            "secret": decrypt_string(encrypted_secret, user_id)
        }
    return None

# === Get all registered user IDs ===
def get_all_user_ids():
    try:
        users = firebase.database().child("users").get()
        return [user.key() for user in users.each()] if users.each() else []
    except Exception as e:
        print(f"❌ Failed to fetch user IDs: {e}")
        return []

# === Get saved Kraken API keys for a user ===
def get_api_keys(user_id):
    try:
        keys = firebase.database().child("users").child(user_id).child("api_keys").child("kraken").get()
        return keys.val() if keys.val() else None
    except Exception as e:
        print(f"❌ Failed to fetch API keys for {user_id}: {e}")
        return None

def save_strategy_config(user_id, config, token, mode):
    db = firebase.database()
    try:
        db.child("users").child(user_id).child(mode).child("settings").child("strategy_config").set(config, token)
        print(f"✅ Saved strategy config for {user_id}")
    except Exception as e:
        print(f"❌ Failed to save strategy config: {e}")

# === Get user's saved strategy config ===
def load_strategy_config(user_id, token, mode):
    db = firebase.database()
    try:
        data = db.child("users").child(user_id).child(mode).child("settings").child("strategy_config").get(token).val()
        if data:
            return data
        else:
            print(f"⚠️ No strategy config found for {user_id}")
            return {}
    except Exception as e:
        print(f"❌ Failed to load strategy config: {e}")
        return {}

def save_portfolio_snapshot_to_firebase(user_id, snapshot, token, mode):
    db = firebase.database()
    try:
        db.child("users").child(user_id).child(mode).child("balances").child("portfolio_snapshot").set(snapshot, token)
        print(f"✅ Saved snapshot to Firebase for {user_id}")
    except Exception as e:
        print(f"❌ Failed to save snapshot to Firebase: {e}")

def load_portfolio_snapshot_from_firebase(user_id, token, mode):
    db = firebase.database()
    try:
        data = db.child("users").child(user_id).child(mode).child("balances").child("portfolio_snapshot").get(token).val()
        if data:
            print(f"📥 Loaded portfolio snapshot for {user_id}")
            return data
        else:
            print(f"⚠️ No portfolio snapshot found for {user_id}")
            return {}
    except Exception as e:
        print(f"❌ Failed to load snapshot from Firebase: {e}")
        return {}

def load_user_data(user_id, path, mode):
    db = firebase.database()
    token = st.session_state.user.get("token")
    try:
        data = db.child("users").child(user_id).child(mode).child(path).get(token).val()
        return data if data else {}
    except Exception as e:
        print(f"❌ Failed to load user data from {path}: {e}")
        return {}

def save_user_data(user_id, path, data, mode):
    db = firebase.database()
    token = st.session_state.user.get("token")
    try:
        db.child("users").child(user_id).child(mode).child(path).set(data, token)
        print(f"✅ Saved user data to {path}")
    except Exception as e:
        print(f"❌ Failed to save user data to {path}: {e}")

def load_firebase_json(path, mode, user_id):
    return load_user_data(user_id, path, mode)

def save_firebase_json(path, data, mode, user_id):
    return save_user_data(user_id, path, data, mode)

def list_firebase_files(path, mode, user_id):
    db = firebase.database()
    token = st.session_state.user.get("token")
    try:
        data = db.child("users").child(user_id).child(mode).child(path).get(token)
        if data.each():
            return [item.key() for item in data.each()]
        return []
    except Exception as e:
        print(f"❌ Failed to list files at {path}: {e}")
        return []

def get_firebase_data(user_id, key, subfolder, mode, token=None):
    url = f"{FIREBASE_BASE_URL}/users/{user_id}/{subfolder}/{key}.json"
    if token:
        url += f"?auth={token}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Firebase load failed: {response.text}")
        return {}
