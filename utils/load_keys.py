import streamlit as st
from utils.encryption import decrypt_string
from utils.firebase_config import firebase

def load_user_api_keys(user_id, exchange, token=None):
    path = f"users/{user_id}/api_keys/{exchange}"
    data = firebase.database().child("users").child(user_id).child("api_keys").child(exchange).get(token).val()

    if not data:
        return {}

    key = decrypt_string(data.get("public"), user_id)
    secret = decrypt_string(data.get("private"), user_id)
    return {
        "key": key,
        "secret": secret
    }

def api_keys_exist(user_id, token, exchange="kraken"):
    keys = load_user_api_keys(user_id, exchange, token)
    return bool(keys and keys.get("key") and keys.get("secret"))
