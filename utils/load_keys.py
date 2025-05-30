import requests
import streamlit as st
from utils.firebase_config import firebase

def load_api_keys(user_id):
    """
    Loads Kraken API keys from Firebase for the given user.
    """
    try:
        token = st.session_state.user["token"]
        ref = firebase.database().child("users").child(user_id).child("api_keys").child("kraken")
        data = ref.get(token).val()

        if not data or "key" not in data or "secret" not in data:
            return None  # 🔄 Return None if keys are missing

        return {
            "key": data["key"],
            "secret": data["secret"]
        }
    except KeyError:
        return None
    except Exception as e:
        st.warning(f"⚠️ Failed to load API keys: {e}")
        return None

def api_keys_exist(user_id):
    """
    Checks if Kraken API keys are present in Firebase for the given user.
    """
    keys = load_api_keys(user_id)
    return bool(keys and keys.get("key") and keys.get("secret"))
