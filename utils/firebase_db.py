
import requests
from utils.encryption_utils import encrypt_string, decrypt_string
from utils.firebase_config import firebase

# Get the Realtime Database URL from your config
DATABASE_URL = firebase_project_info["databaseURL"]

def save_user_profile(user_id, name, email, token):
    """
    Save user profile to Firebase Realtime Database.
    """
    url = f"{DATABASE_URL}/users/{user_id}.json?auth={token}"
    data = {
        "name": name,
        "email": email
    }
    response = requests.put(url, json=data)
    response.raise_for_status()
    return response.json()

def load_user_profile(user_id, token):
    """
    Load user profile from Firebase Realtime Database.
    """
    url = f"{DATABASE_URL}/users/{user_id}.json?auth={token}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def save_user_api_keys(user_id, exchange, api_key, api_secret):
    encrypted_key = encrypt_string(api_key)
    encrypted_secret = encrypt_string(api_secret)

    token = st.session_state.user["token"]
    db = firebase.database()
    db.child("api_keys").child(user_id).child(exchange).set({
        "key": encrypted_key,
        "secret": encrypted_secret
    }, token)

def load_user_api_keys(user_id, exchange):
    token = st.session_state.user["token"]
    db = firebase.database()
    result = db.child("api_keys").child(user_id).child(exchange).get(token)
    if result.val():
        encrypted_key = result.val().get("key", "")
        encrypted_secret = result.val().get("secret", "")
        return {
            "key": decrypt_string(encrypted_key),
            "secret": decrypt_string(encrypted_secret)
        }
    return None
