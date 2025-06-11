import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    st.title("🔐 Welcome to BitPanel")
    st.markdown("#### Please log in to continue")

    
    # Get user input
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In"):
            try:
                user = sign_in(email, password)  # use local `email` from input
                user_id = user["localId"]
                token = user["idToken"]

                # Load profile from Firebase Realtime DB
                profile = load_user_profile(user_id, token) or {}

                # Store only clean user info into session_state
                st.session_state.user = {
                    "email": email,
                    "token": token,
                    "name": profile.get("name", "User"),
                    "localId": user_id
                }

                st.session_state.token = token
                
                st.success("✅ Login successful!")
                st.session_state.page = "📊 Portfolio"
                st.session_state.current_page = "📊 Portfolio"
                st.experimental_rerun()
                
            except Exception as e:
                st.error("❌ Invalid email or password. Try again.")
                st.exception(e)

    with col2:
        if st.button("Create Account"):
            st.session_state.page = "signup"
            st.rerun()

        # Forgot Password button
        if st.button("🔑 Forgot Password?"):
            st.session_state.reset_email = email  # pre-fill on next page
            st.session_state.page = "reset_password"
            st.rerun()   
