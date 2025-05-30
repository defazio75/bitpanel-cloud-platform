from utils.firebase_config import firebase

def initialize_user_structure(user_id, token):
    db = firebase.database()

    # Base user data
    db.child("users").child(user_id).child("api_keys").set({}, token)
    db.child("users").child(user_id).child("settings").set({}, token)

    # Allocation data
    db.child("users").child(user_id).child("strategy_allocations").child("paper").set({}, token)
    db.child("users").child(user_id).child("strategy_allocations").child("live").set({}, token)
    db.child("users").child(user_id).child("coin_allocations").child("paper").set({}, token)

    # Bot runtime and performance data
    for mode in ["paper", "live"]:
        db.child("users").child(user_id).child(mode).child("current").set({}, token)
        db.child("users").child(user_id).child(mode).child("performance").set({}, token)
        db.child("users").child(user_id).child(mode).child("history").set({}, token)
        db.child("users").child(user_id).child(mode).child("balances").set({}, token)
        db.child("users").child(user_id).child(mode).child("trade_logs").set({}, token)

    print(f"✅ Firebase structure initialized for user: {user_id}")
