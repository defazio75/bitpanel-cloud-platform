import requests
import streamlit as st
from utils.firebase_config import firebase
from utils.firebase_db import load_user_api_keys

def load_api_keys(user_id):
    """
    Loads decrypted Kraken API keys from Firebase.
    """
    try:
        return load_user_api_keys(user_id, "kraken")  # ✅ Decrypts internally
    except Exception as e:
        st.warning(f"⚠️ Failed to load API keys: {e}")
        return None

def api_keys_exist(user_id):
    """
    Checks if decrypted API keys exist for the user.
    """
    keys = load_api_keys(user_id)
    return bool(keys and keys.get("key") and keys.get("secret"))
