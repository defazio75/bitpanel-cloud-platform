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
    
    sign_in_methods = data.get("signinMethods", [])
    print("Sign-in methods:", sign_in_methods)  # Debug

    return "password" in sign_in_methods

