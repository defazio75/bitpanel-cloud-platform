import streamlit as st
from utils.firebase_db import load_user_api_keys

def load_api_keys(user_id):
    token = st.session_state.user["token"]
    db = firebase.database()
    data = db.child("api_keys").child(user_id).child("kraken").get(token).val()

    if not data or "key" not in data or "secret" not in data:
        raise ValueError("❌ Kraken API keys not found in Firebase.")

    return {
        "key": data["key"],
        "secret": data["secret"]
    }


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
