from utils.encryption import decrypt_string
from utils.firebase_config import firebase

def load_user_api_keys(user_id, exchange, token=None):
    try:
        if not token:
            print(f"⚠️ Missing token for user {user_id} – skipping API key load.")
            return {}

        path = f"users/{user_id}/api_keys/{exchange}"
        result = firebase.database().child("users").child(user_id).child("api_keys").child(exchange).get(token)

        if not result.each() and not result.val():
            print(f"⚠️ No API key data found at {path}")
            return {}

        data = result.val()
        key = decrypt_string(data.get("public", ""), user_id)
        secret = decrypt_string(data.get("private", ""), user_id)

        if not key or not secret:
            print(f"⚠️ Decryption failed or missing values for {user_id} on {exchange}")
            return {}

        return {
            "key": key,
            "secret": secret
        }

    except Exception as e:
        print(f"❌ Error loading API keys for {user_id} ({exchange}): {e}")
        return {}

def api_keys_exist(user_id, token, exchange="kraken"):
    keys = load_user_api_keys(user_id, exchange, token)
    return bool(keys and keys.get("key") and keys.get("secret"))
