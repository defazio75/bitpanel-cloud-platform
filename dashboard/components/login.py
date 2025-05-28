import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    st.set_page_config(page_title="BitPanel Login", layout="centered")
    st.title("🔐 Welcome to BitPanel")

    st.markdown("#### Please log in to continue")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In"):
            try:
                user = sign_in(email, password)
                st.session_state.user = user
                st.success("✅ Login successful!")
                st.experimental_rerun()
            except Exception as e:
                st.error("❌ Invalid email or password. Try again.")

    with col2:
        if st.button("Create Account"):
            st.session_state.page = "signup"
            st.experimental_rerun()
