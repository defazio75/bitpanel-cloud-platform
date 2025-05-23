import configparser
import os

# Define key file location
key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "Kraken.key"))

def prompt_for_api_keys():
    print("🔐 No API key found. Please enter your Kraken credentials.")
    api_key = input("Enter API Key: ").strip()
    api_secret = input("Enter API Secret: ").strip()
    print("🟡 PROMPT FUNCTION TRIGGERED")

    config = configparser.ConfigParser()
    config['API'] = {
        'api_key': api_key,
        'api_secret': api_secret
    }

    os.makedirs(os.path.dirname(key_path), exist_ok=True)
    with open(key_path, 'w') as configfile:
        config.write(configfile)
    print("✅ API key saved. You're ready to go!")

def _load_api_keys_once():
    config = configparser.ConfigParser()

    if not os.path.exists(key_path):
        prompt_for_api_keys()

    config.read(key_path)

    if "API" not in config:
        print("⚠️ Missing [API] section in Kraken.key. Prompting for re-entry.")
        prompt_for_api_keys()
        config.read(key_path)

    api_key = config['API'].get('api_key', '').strip()
    api_secret = config['API'].get('api_secret', '').strip()

    if not api_key or not api_secret:
        print("⚠️ Empty API Key or Secret found. Prompting for re-entry.")
        prompt_for_api_keys()
        config.read(key_path)
        api_key = config['API']['api_key'].strip()
        api_secret = config['API']['api_secret'].strip()

    return api_key, api_secret

def api_keys_exist():
    import configparser, os
    config_path = os.path.join("config", "Kraken.key")
    if not os.path.exists(config_path):
        return False
    config = configparser.ConfigParser()
    config.read(config_path)
    return config.has_option("API", "api_key") and config.get("API", "api_key") not in ["", "your_actual_key_here"]

# 🔐 Load once and share
API_KEY, API_SECRET = _load_api_keys_once()

# ✅ Optional: clean debug line only if run standalone
if __name__ == "__main__":
    pass
