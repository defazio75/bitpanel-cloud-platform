import requests
from utils.firebase_config import firebase_api_key

FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

def sign_in(email, password):
    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={firebase_api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def sign_up(email, password):
    url = f"{FIREBASE_AUTH_URL}:signUp?key={firebase_api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def check_user_exists(email):
    url = f"{FIREBASE_AUTH_URL}:createAuthUri?key={firebase_api_key}"
    payload = {"identifier": email, "continueUri": "http://localhost"}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return bool(data.get("registered", False))

def save_user_profile(user_id, name, email, token):
    db = firebase.database()
    db.child("users").child(user_id).set({
        "name": name,
        "email": email
    }, token)

def load_user_profile(user_id, token):
    db = firebase.database()
    return db.child("users").child(user_id).get(token).val()
