import os
import json
from config.config import get_mode
from utils.firebase_db import (
    load_strategy_state,
    save_strategy_state,
)
from utils.json_utils import (
    load_coin_state,
    save_bot_state,
)

# === GLOBAL TOGGLE: Set to True to use Firebase ===
USE_FIREBASE = True

def load_state(user_id, coin, strategy, mode=None):
    if not mode:
        mode = get_mode()
    
    if USE_FIREBASE:
        return load_strategy_state(user_id, coin, strategy, mode)
    else:
        return load_coin_state(user_id, coin, mode).get(strategy, {})

def save_state(user_id, coin, strategy, new_state, mode=None):
    if not mode:
        mode = get_mode()

    if USE_FIREBASE:
        save_strategy_state(user_id, coin, strategy, new_state, mode)
    else:
        save_bot_state(user_id, coin, strategy, new_state, mode)
