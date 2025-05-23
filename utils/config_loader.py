# /utils/config_loader.py
# This file now only contains utility to retrieve bot-level settings from settings.json

import json
import os

SETTINGS_PATH = os.path.join("config", "settings.json")

def get_setting(category, bot_name):
    try:
        with open(SETTINGS_PATH, "r") as f:
            data = json.load(f)
        return data.get(category, {}).get(bot_name)
    except Exception as e:
        print(f"⚠️ Error loading setting for {category}/{bot_name}: {e}")
        return None
