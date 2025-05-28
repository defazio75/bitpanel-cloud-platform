import os
import json

API_KEY_DIR = "data/api_keys"

def get_api_key_path(user_id, exchange):
    """
    Returns the path to the API key file for the specified user and exchange.
    """
    filename = f"{user_id}_{exchange.lower()}.json"
    return os.path.join(API_KEY_DIR, filename)

def save_api_keys(user_id, exchange, api_key, api_secret):
    """
    Saves API keys securely for a given user and exchange.
    """
    os.makedirs(API_KEY_DIR, exist_ok=True)
    path = get_api_key_path(user_id, exchange)
    with open(path, "w") as f:
        json.dump({
            "api_key": api_key,
            "api_secret": api_secret
        }, f)

def load_api_keys(user_id, exchange):
    """
    Loads API keys for a given user and exchange.
    Returns None if not found.
    """
    path = get_api_key_path(user_id, exchange)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None
