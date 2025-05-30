import os
from cryptography.fernet import Fernet

def load_encryption_key():
    try:
        with open("/etc/secrets/encryption.key", "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError("❌ encryption.key file not found in /etc/secrets")

def encrypt_string(plain_text):
    key = load_encryption_key()
    f = Fernet(key)
    return f.encrypt(plain_text.encode()).decode()

def decrypt_string(encrypted_text):
    key = load_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_text.encode()).decode()
