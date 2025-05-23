import os
import json
import streamlit as st

def _load_api_keys_once():
    if "user" not in st.session_state:
        raise RuntimeError("User must be logged in to access API keys.")

    user_id = st.session_state.user['localId']
    key_path = f"config/{user_id}/kraken_keys.json"

    if not os.path.exists(key_path):
        raise FileNotFoundError("API key file not found. Please add your keys in Settings or switch to paper mode.")

    with open(key_path, "r") as f:
        data = json.load(f)

    api_key = data.get("api_key", "").strip()
    api_secret = data.get("api_secret", "").strip()

    if not api_key or not api_secret:
        raise ValueError("API keys found but are empty. Please re-enter them.")

    return api_key, api_secret

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
