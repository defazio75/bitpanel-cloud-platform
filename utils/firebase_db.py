import streamlit as st
import requests
from utils.encryption import encrypt_string, decrypt_string
from utils.firebase_config import firebase
import pyrebase
from utils.firebase_config import firebase

def save_user_profile(user_id, name, email, token):
    """
    Save user profile to Firebase Realtime Database using Pyrebase.
    """
    db = firebase.database()
    db.child("users").child(user_id).set({
        "name": name,
        "email": email
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
    encrypted_key = encrypt_string(api_key)
    encrypted_secret = encrypt_string(api_secret)

    token = st.session_state.user["token"]
    db = firebase.database()
    db.child("api_keys").child(user_id).child(exchange).set({
        "key": encrypted_key,
        "secret": encrypted_secret
    }, token)

def load_user_api_keys(user_id, exchange):
    token = st.session_state.user["token"]
    db = firebase.database()
    result = db.child("api_keys").child(user_id).child(exchange).get(token)
    if result.val():
        encrypted_key = result.val().get("key", "")
        encrypted_secret = result.val().get("secret", "")
        return {
            "key": decrypt_string(encrypted_key),
            "secret": decrypt_string(encrypted_secret)
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
        keys = firebase.database().child("api_keys").child(user_id).child("kraken").get()
        return keys.val() if keys.val() else None
    except Exception as e:
        print(f"❌ Failed to fetch API keys for {user_id}: {e}")
        return None

# === Get user's saved strategy config ===
def load_strategy_config(user_id):
    try:
        config = firebase.database().child("users").child(user_id).child("strategies").get()
        return config.val() if config.val() else {}
    except Exception as e:
        print(f"❌ Failed to load strategy config for {user_id}: {e}")
        return {}

def save_portfolio_snapshot_to_firebase(user_id, snapshot, token):
    from utils.firebase_config import firebase
    db = firebase.database()
    try:
        db.child("portfolio_snapshots").child(user_id).set(snapshot, token)
        print(f"✅ Saved snapshot to Firebase for {user_id}")
    except Exception as e:
        print(f"❌ Failed to save snapshot to Firebase: {e}")

def load_portfolio_snapshot_from_firebase(user_id, token):
    from utils.firebase_config import firebase
    db = firebase.database()
    try:
        data = db.child("portfolio_snapshots").child(user_id).get(token).val()
        if data:
            print(f"📥 Loaded portfolio snapshot for {user_id}")
            return data
        else:
            print(f"⚠️ No portfolio snapshot found for {user_id}")
            return {}
    except Exception as e:
        print(f"❌ Failed to load snapshot from Firebase: {e}")
        return {}
