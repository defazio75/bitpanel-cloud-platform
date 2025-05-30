def initialize_user_structure(user_id, token, name, email, signup_date):
    from utils.firebase_config import firebase

    db = firebase.database()

    # Set up the user's root profile info
    db.child("users").child(user_id).set({
        "name": name,
        "email": email,
        "signup_date": signup_date,
        "api_keys": {},  # optional initial placeholders
        "settings": {},
        "strategy_allocations": {
            "paper": {},
            "live": {}
        },
        "coin_allocations": {
            "paper": {}
        },
        "paper": {
            "current": {},
            "performance": {},
            "history": {},
            "balances": {},
            "trade_logs": {}
        },
        "live": {
            "current": {},
            "performance": {},
            "history": {},
            "balances": {},
            "trade_logs": {}
        }
    }, token)
