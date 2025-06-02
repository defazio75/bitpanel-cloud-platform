import os
import base64
import hashlib
from cryptography.fernet import Fernet

# Load the master key securely from environment or file
def load_master_secret():
    try:
        with open("/etc/secrets/encryption.key", "rb") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError("❌ Master encryption key not found in /etc/secrets")

# Derive per-user encryption key from master secret and user_id
def get_user_key(user_id):
    master_secret = load_master_secret()
    composite = master_secret + user_id.encode()
    hashed = hashlib.sha256(composite).digest()
    return base64.urlsafe_b64encode(hashed[:32])  # Fernet requires 32-byte base64 key

# Encrypt using user-specific key
def encrypt_string(plain_text, user_id):
    key = get_user_key(user_id)
    f = Fernet(key)
    return f.encrypt(plain_text.encode()).decode()

# Decrypt using user-specific key
def decrypt_string(encrypted_text, user_id):
    key = get_user_key(user_id)
    f = Fernet(key)
    return f.decrypt(encrypted_text.encode()).decode()
