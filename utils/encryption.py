from cryptography.fernet import Fernet
import os

# Load encryption key from file
def load_encryption_key():
    key_path = os.path.join("config", "encryption.key")
    with open(key_path, "rb") as f:
        return f.read()

# Encrypt a string (like an API key or secret)
def encrypt_string(plain_text):
    key = load_encryption_key()
    fernet = Fernet(key)
    return fernet.encrypt(plain_text.encode()).decode()

# Decrypt a string
def decrypt_string(encrypted_text):
    key = load_encryption_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_text.encode()).decode()
