from utils.firebase_config import firebase

# Expose db globally
db = firebase.database()

def initialize_user_structure(user_id, token, name, email, signup_date):
    # Set up the user's root structure
    db.child("users").child(user_id).set({
        "profile": {
            "name": name,
            "email": email,
            "signup_date": signup_date,
            "payment_info": {}  # placeholder for future billing data
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
