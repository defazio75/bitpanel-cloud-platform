import os
from cryptography.fernet import Fernet

# Path to the secret file (Render mounts it in /etc/secrets if named `encryption.key`)
ENCRYPTION_KEY_PATH = "/etc/secrets/encryption.key"

# Read and load the key
try:
    with open(ENCRYPTION_KEY_PATH, "rb") as f:
        ENCRYPTION_KEY = f.read().strip()
except FileNotFoundError:
    raise FileNotFoundError("❌ encryption.key file not found in /etc/secrets")

fernet = Fernet(ENCRYPTION_KEY)

def encrypt_string(plain_text):
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_string(encrypted_text):
    return fernet.decrypt(encrypted_text.encode()).decode()
