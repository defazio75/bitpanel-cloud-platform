import streamlit as st
from utils.firebase_db import load_user_api_keys

def load_api_keys():
    """
    Loads API keys for the logged-in user from Firebase (Live or Paper mode).
    Always pulls from Firebase. Paper mode runs without keys.
    """
    if "user" not in st.session_state:
        raise RuntimeError("User must be logged in to access API keys.")

    user_id = st.session_state.user.get("localId") or st.session_state.user.get("id")
    return load_user_api_keys(user_id, "kraken")


def api_keys_exist():
    """
    Returns True if both API key and secret are present in Firebase.
    Used to determine whether live mode can be enabled.
    """
    try:
        keys = load_api_keys()
        return bool(keys.get("key")) and bool(keys.get("secret"))
    except:
        return False
