
import requests
from utils.firebase_config import firebase_project_info

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

def save_user_api_keys(user_id, token, exchange, api_key, api_secret):
    db = firebase.database()
    encrypted = {
        "api_key": encrypt(api_key),       # You’ll define `encrypt()` next
        "api_secret": encrypt(api_secret)
    }
    db.child("users").child(user_id).child("api_keys").child(exchange).set(encrypted, token)

def load_user_api_keys(user_id, token, exchange):
    db = firebase.database()
    result = db.child("users").child(user_id).child("api_keys").child(exchange).get(token)
    if result.val():
        decrypted = {
            "api_key": decrypt(result.val()["api_key"]),
            "api_secret": decrypt(result.val()["api_secret"])
        }
        return decrypted
    return None
