import streamlit as st
from utils.firebase_auth import sign_up
from utils.firebase_setup import initialize_user_structure
from datetime import datetime
from utils.firebase_db import save_user_profile

def signup():
    st.title("🆕 Create Your BitPanel Account")

    name = st.text_input("Full Name", key="signup_name")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

    if st.button("Create Account"):
        if not name or not email or not password:
            st.error("All fields are required.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                user = sign_up(email, password)
                user["name"] = name
                st.session_state.user = user

                # Initialize Firebase structure
                user_id = user["localId"]
                token = user["idToken"]
                
                initialize_user_structure(
                    user_id=user_id,
                    name=name,
                    email=email,
                    token=token,
                    signup_date=datetime.utcnow().isoformat()
                )

                st.success("✅ Account created successfully!")
                st.session_state.page = "login"
                st.experimental_rerun()
                
            except Exception as e:
                st.error("❌ Account creation failed. Email may already be in use.")

    if st.button("← Back to Login"):
        st.session_state.page = "login"
        st.experimental_rerun()
