import streamlit as st
import requests

from utils.firebase_auth import (
    sign_in,
    sign_up,
    check_user_exists
)

from utils.firebase_db import (
    save_user_profile,
    load_user_profile
)

def login():
    st.subheader("🔐 BitPanel Login")

    # Initialize stage
    if "stage" not in st.session_state:
        st.session_state.stage = "email"
    if "email" not in st.session_state:
        st.session_state.email = ""

    # === STEP 1: Enter Email ===
    if st.session_state.stage == "email":
        st.markdown("### 📧 Enter Your Email")
        email_input = st.text_input("Email", key="email_input")

        if st.button("Continue") and email_input:
            st.session_state.email = email_input
            
            try:
                if check_user_exists(email_input):
                    st.session_state.stage = "login"
                else:
                    st.session_state.stage = "signup"
                st.rerun()
                
            except requests.exceptions.HTTPError as e:
                st.error("❌ Firebase API error when checking account.")
                st.exception(e)

            except Exception as e:
                st.error("❌ Unexpected error during user check.")
                st.exception(e)

    # === STEP 2A: Log In ===
    elif st.session_state.stage == "login":
        st.markdown(f"**Welcome back, {st.session_state.email}**")
        password = st.text_input("Password", type="password")

        if st.button("Log In"):
            try:
                user = sign_in(st.session_state.email, password)
                user_id = user['localId']
                token = user['idToken']
                profile = load_user_profile(user_id, token)

                st.session_state.user = {
                    "id": user_id,
                    "token": token,
                    "email": st.session_state.email,
                    "name": profile.get("name", "No Name") if profile else "No Name"
                }

                st.success("✅ Logged in successfully!")
                st.rerun()
            except Exception as e:
                err_str = str(e)
                if "INVALID_PASSWORD" in err_str:
                    st.error("❌ Incorrect password.")
                elif "INVALID_LOGIN_CREDENTIALS" in err_str:
                    st.error("❌ This account does not support password login.")
                    st.info("Try creating a new account or logging in with another method.")
                    if st.button("🔙 Back to Email Entry"):
                        st.session_state.stage = "email"
                        st.rerun()
                elif "EMAIL_NOT_FOUND" in err_str:
                    st.warning("⚠️ Email not found. Redirecting to Sign Up...")
                    st.session_state.stage = "signup"
                    st.rerun()

    # === STEP 2B: Sign Up ===
    elif st.session_state.stage == "signup":
        st.markdown(f"**Create an account for {st.session_state.email}**")
        name = st.text_input("Full Name")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if password != confirm:
                st.error("❌ Passwords do not match.")
            elif not name:
                st.error("❌ Name is required.")
            else:
                try:
                    user = sign_up(st.session_state.email, password)
                    user_id = user['localId']
                    token = user['idToken']

                    save_user_profile(user_id, name, st.session_state.email, token)

                    st.session_state.user = {
                        "id": user_id,
                        "token": token,
                        "email": st.session_state.email,
                        "name": name
                    }

                    st.success("✅ Account created and logged in!")
                    st.rerun()
                except requests.exceptions.HTTPError as e:
                    if "EMAIL_EXISTS" in str(e):
                        st.warning("⚠️ Email already registered. Redirecting to login...")
                        st.session_state.stage = "login"
                        st.rerun()
                    else:
                        st.error("Signup failed.")
                        st.exception(e)
