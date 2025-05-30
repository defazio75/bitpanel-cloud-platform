import requests
import streamlit as st
from utils.firebase_config import firebase, auth

def load_api_keys(user_id):
    """
    Loads Kraken API keys from Firebase for the given user.
    Requires that st.session_state.user['token'] is set.
    """
    try:
        token = st.session_state.user["token"]
        ref = firebase.database().child("users").child(user_id).child("api_keys").child("kraken")
        result = ref.get(token).val()

        if not result or "key" not in result or "secret" not in result:
            raise ValueError("❌ Kraken API keys not found in Firebase.")

        return {
            "key": result["key"],
            "secret": result["secret"]
        }
    except KeyError:
        raise ValueError("❌ User not authenticated. Missing session token.")
    except Exception as e:
        raise ValueError(f"❌ Failed to load API keys: {e}")

def api_keys_exist(user_id):
    """
    Checks if Kraken API keys are present in Firebase for the given user.
    """
    try:
        keys = load_api_keys(user_id=user_id)
        return bool(keys.get("key")) and bool(keys.get("secret"))
    except Exception:
        return False
