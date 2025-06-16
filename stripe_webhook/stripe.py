import os
import stripe
from flask import Flask, request, jsonify
import json
import firebase_admin
from firebase_admin import credentials, firestore

# === Initialize Firebase ===
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

db = firestore.client()

# === Initialize Flask + Stripe ===
app = Flask(__name__)
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
endpoint_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

@app.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except stripe.error.SignatureVerificationError:
        return "Invalid signature", 400

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data["metadata"]["user_id"]
        customer_id = data.get("customer")
        plan_id = data["items"]["data"][0]["price"]["id"]

        plan_name = {
            "price_123_starter": "starter",
            "price_123_pro": "pro",
            "price_123_annual": "pro_annual"
        }.get(plan_id, "unknown")
                
        if plan_name == "unknown":
            print(f"⚠️ Unknown plan ID received: {plan_id}")

        trial_end = data.get("subscription", {}).get("trial_end")
        trial_timestamp = firestore.SERVER_TIMESTAMP if not trial_end else firestore.Timestamp.from_seconds(trial_end)

        # Save to Firebase
        if user_id:
            db.collection("users").document(user_id).update({
                "profile.billing": {
                    "subscription_status": "active",
                    "stripe_customer_id": customer_id,
                    "plan": plan_name,
                    "trial_end_date": trial_timestamp
                }
            })
            print(f"✅ Subscription updated for {user_id}")

    elif event_type == "customer.subscription.deleted":
        customer_id = data.get("customer")
        docs = db.collection("users").where("profile.billing.stripe_customer_id", "==", customer_id).stream()
        for doc in docs:
            db.collection("users").document(doc.id).update({
                "profile.billing.subscription_status": "canceled"
            })
            print(f"⚠️ Subscription canceled for {doc.id}")

    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        docs = db.collection("users").where("profile.billing.stripe_customer_id", "==", customer_id).stream()
        for doc in docs:
            db.collection("users").document(doc.id).update({
                "profile.billing.subscription_status": "past_due"
            })
            print(f"⚠️ Payment failed for {doc.id}")
            
    return jsonify(success=True), 200
