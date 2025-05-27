
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
