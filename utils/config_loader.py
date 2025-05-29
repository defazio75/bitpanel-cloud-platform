# /utils/config_loader.py
# This file now only contains utility to retrieve bot-level settings from settings.json

import json
import os

def get_settings_path(user_id):
    return os.path.join("config", user_id, "settings.json")

def get_setting(category, bot_name, user_id, default=None):
    path = get_settings_path(user_id)
    try:
        with open(SETTINGS_PATH, "r") as f:
            data = json.load(f)
        return data.get(category, {}).get(bot_name)
    except Exception as e:
        print(f"⚠️ Error loading setting for {category}/{bot_name} ({user_id}): {e}")
        return None
