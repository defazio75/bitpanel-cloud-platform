import time
import requests
import base64
import hashlib
import hmac
from urllib.parse import urlencode
from utils.load_keys import load_user_api_keys
from utils.firebase_config import auth  # Needed if using token-based auth with Firebase

API_URL = "https://api.kraken.com"

def rate_limited_query_private(endpoint, data=None, user_id=None):
    if data is None:
        data = {}

    # Load encrypted keys
    keys = load_user_api_keys(user_id, "kraken", token=auth.current_user['idToken'])
    api_key = keys["key"]
    api_secret = keys["secret"]

    # Prepare headers
    nonce = str(int(1000 * time.time()))
    data["nonce"] = nonce
    post_data = urlencode(data)

    # Message signing
    message = (nonce + post_data).encode()
    sha256 = hashlib.sha256(message).digest()
    path = f"/0/private/{endpoint.split('/')[-1]}"
    secret_decoded = base64.b64decode(api_secret)
    signature = hmac.new(secret_decoded, path.encode() + sha256, hashlib.sha512)
    sig_digest = base64.b64encode(signature.digest())

    headers = {
        "API-Key": api_key,
        "API-Sign": sig_digest.decode()
    }

    url = f"{API_URL}{endpoint}"
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()
