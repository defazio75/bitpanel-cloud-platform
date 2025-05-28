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

    # Optional: Show debug if Streamlit is available
    try:
        import streamlit as st
        st.write("DEBUG - Firebase response:", data)
    except ImportError:
        pass  # Ignore if streamlit isn't available in this context

    print("DEBUG - Firebase response:", data)
    
    sign_in_methods = data.get("signinMethods", [])
    return "password" in sign_in_methods

def send_password_reset(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={firebase_api_key}"
    payload = {
        "requestType": "PASSWORD_RESET",
        "email": email
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

