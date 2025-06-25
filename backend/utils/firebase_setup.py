from utils.firebase_config import firebase

# Expose db globally
db = firebase.database()

def initialize_user_structure(user_id, token, name, email, signup_date):
    db.child("users").child(user_id).set({
        "profile": {
            "account": {
                "name": name,
                "email": email,
                "signup_date": signup_date,
                "role": "user",          # default role
                "paid": False,           # default unpaid status
                "bypass": False          # default no bypass
            }
        },
        "api_keys": {},  # Placeholder
        "paper": {
            "strategy_allocations": {},
            "coin_allocations": {},
            "current": {},
            "performance": {},
            "history": {},
            "balances": {},
            "trade_logs": {}
        },
        "live": {
            "strategy_allocations": {},
            "current": {},
            "performance": {},
            "history": {},
            "balances": {},
            "trade_logs": {}
        }
    }, token)
