import json
import os

# === Base Save Utility ===
def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# === Base Load Utility ===
def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

# === User-Aware Helpers ===
def get_user_data_path(user_id, subfolder, filename, mode="paper"):
    base_dir = f"data/json_{mode}/{user_id}/{subfolder}"
    return os.path.join(base_dir, filename)

def save_user_state(user_id, subfolder, filename, data, mode="paper"):
    path = get_user_data_path(user_id, subfolder, filename, mode)
    save_json(path, data)

def load_user_state(user_id, subfolder, filename, mode="paper"):
    path = get_user_data_path(user_id, subfolder, filename, mode)
    return load_json(path)
