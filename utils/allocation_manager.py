import os
import json

def load_allocations(user_id, mode="paper"):
    path = os.path.join("data", f"json_{mode}", user_id, "portfolio", "coin_allocations.json")
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading allocations for {user_id}: {e}")
        return {}

def save_allocations(user_id, allocations, mode="paper"):
    path = os.path.join("data", f"json_{mode}", user_id, "portfolio")
    os.makedirs(path, exist_ok=True)

    full_path = os.path.join(path, "coin_allocations.json")
    try:
        with open(full_path, "w") as f:
            json.dump(allocations, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving allocations for {user_id}: {e}")
