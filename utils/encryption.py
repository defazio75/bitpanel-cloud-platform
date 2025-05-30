import os
from cryptography.fernet import Fernet

def load_encryption_key():
    # Read from Render secret environment variable
    key = os.environ.get("ENCRYPTION_KEY")
    if not key:
        raise ValueError("❌ ENCRYPTION_KEY environment variable not set.")
    return key.encode()  # Convert to bytes

def encrypt_string(plain_text):
    key = load_encryption_key()
    f = Fernet(key)
    return f.encrypt(plain_text.encode()).decode()

def decrypt_string(encrypted_text):
    key = load_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_text.encode()).decode()
