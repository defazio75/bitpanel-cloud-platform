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
def get_user_encryption_key(user_id):
    """
    Derives a user-specific encryption key from the master key + user_id.
    """
    try:
        with open("/etc/secrets/encryption.key", "rb") as f:
            master_key = f.read()
    except FileNotFoundError:
        raise FileNotFoundError("❌ encryption.key file not found in /etc/secrets")

    # Combine master key + user_id into a consistent 32-byte key
    derived_key = hashlib.pbkdf2_hmac('sha256', user_id.encode(), master_key, 100000, dklen=32)
    return base64.urlsafe_b64encode(derived_key)

# Encrypt using user-specific key
def encrypt_string(plain_text, user_id):
    key = get_user_encryption_key(user_id)
    f = Fernet(key)
    return f.encrypt(plain_text.encode()).decode()

# Decrypt using user-specific key
def decrypt_string(encrypted_text, user_id):
    key = get_user_encryption_key(user_id)
    f = Fernet(key)
    return f.decrypt(encrypted_text.encode()).decode()
