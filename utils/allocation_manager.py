import json
import os

ALLOCATIONS_PATH = os.path.join('config', 'allocations.json')

def load_allocations():
    if not os.path.exists(ALLOCATIONS_PATH):
        return {}
    with open(ALLOCATIONS_PATH, 'r') as f:
        return json.load(f)

def save_allocations(allocations):
    with open(ALLOCATIONS_PATH, 'w') as f:
        json.dump(allocations, f, indent=4)