import streamlit as st
import requests
from utils.encryption import encrypt_string, decrypt_string
from utils.firebase_config import firebase
import pyrebase
from datetime import datetime

FIREBASE_BASE_URL = "https://bitpanel-967b1-default-rtdb.firebaseio.com"

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
    db = firebase.database()
    result = db.child("users").child(user_id).get(token)
    return result.val() if result.val() else None

def save_user_api_keys(user_id, exchange, api_key, api_secret):
    encrypted_key = encrypt_string(api_key, user_id)
    encrypted_secret = encrypt_string(api_secret, user_id)

    token = st.session_state.user["token"]
    db = firebase.database()
    db.child("users").child(user_id).child("api_keys").child(exchange).set({
        "key": encrypted_key,
        "secret": encrypted_secret
    }, token)

# === STRATEGY CONFIGURATION ===
def save_strategy_allocations(user_id, config, token, mode):
    db = firebase.database()
    db.child("users").child(user_id).child(mode).child("strategy").child("allocations").set(config, token)

def load_strategy_allocations(user_id, token, mode):
    db = firebase.database()
    data = db.child("users").child(user_id).child(mode).child("strategy").child("allocations").get(token).val()
    return data if data else {}

# === PORTFOLIO SNAPSHOT ===
def save_portfolio_snapshot(user_id, snapshot, token, mode):
    db = firebase.database()
    db.child("users").child(user_id).child(mode).child("portfolio").child("portfolio_snapshot").set(snapshot, token)

def load_portfolio_snapshot(user_id, token, mode):
    db = firebase.database()
    data = db.child("users").child(user_id).child(mode).child("portfolio").child("portfolio_snapshot").get(token).val()
    return data if data else {}

# === COIN STATE ===
def save_coin_state(user_id, coin, state_data, token, mode):
    db = firebase.database()
    db.child("users").child(user_id).child(mode).child("current").child(f"{coin}_state").set(state_data, token)

def load_coin_state(user_id, coin, token, mode):
    db = firebase.database()
    data = db.child("users").child(user_id).child(mode).child("current").child(f"{coin}_state").get(token).val()
    return data if data else {}

# === PERFORMANCE HISTORY ===
def save_performance_snapshot(user_id, snapshot, date_str, token, mode):
    db = firebase.database()
    db.child("users").child(user_id).child(mode).child("portfolio").child("history").child(date_str).set(snapshot, token)

def load_performance_snapshot(user_id, date_str, token, mode):
    db = firebase.database()
    data = db.child("users").child(user_id).child(mode).child("portfolio").child("history").child(date_str).get(token).val()
    return data if data else {}

# === FILE LISTING ===
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
