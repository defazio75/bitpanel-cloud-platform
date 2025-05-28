import os
import json
import streamlit as st
from utils.firebase_db import load_user_api_keys

def load_api_keys(mode):
    if "user" not in st.session_state:
        raise RuntimeError("User must be logged in to access API keys.")

    user_id = st.session_state.user.get("localId") or st.session_state.user.get("id")

    if mode == "paper":
        key_path = f"config/{user_id}/kraken_keys.json"
        if not os.path.exists(key_path):
            raise FileNotFoundError("API key file not found. Please add your keys in Settings or switch to paper mode.")
        with open(key_path, "r") as f:
            data = json.load(f)
        api_key = data.get("api_key", "").strip()
        api_secret = data.get("api_secret", "").strip()
        if not api_key or not api_secret:
            raise ValueError("API keys found but are empty. Please re-enter them.")
        return {"key": api_key, "secret": api_secret}

    elif mode == "live":
        return load_user_api_keys(user_id, "kraken")

    else:
        raise ValueError("Mode must be either 'paper' or 'live'.")

def api_keys_exist():
    if "user" not in st.session_state:
        return False

    user_id = st.session_state.user['localId']
    key_path = f"config/{user_id}/kraken_keys.json"

    if not os.path.exists(key_path):
        return False

    try:
        with open(key_path, "r") as f:
            data = json.load(f)
        return bool(data.get("api_key")) and bool(data.get("api_secret"))
    except Exception:
        return False

# Load immediately if in Streamlit and user is set
if "user" in st.session_state:
    API_KEY, API_SECRET = _load_api_keys_once()
else:
    API_KEY = API_SECRET = None  # fallback
