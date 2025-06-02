import streamlit as st
from utils.encryption import decrypt_string
from utils.firebase_config import firebase

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

def api_keys_exist(user_id):
    """
    Checks if decrypted API keys exist for the user.
    """
    keys = get_decrypted_api_keys(user_id, "kraken")
    return bool(keys and keys.get("key") and keys.get("secret"))
