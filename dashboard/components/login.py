import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # Set page layout if not already in app.py
    st.markdown("""
        <style>
        body {
            background-color: #f0f2f6;
        }
        .stApp {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .login-card {
            background: white;
            padding: 2rem 2rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
            text-align: center;
        }
        .login-card h2 {
            margin-bottom: 0.5rem;
        }
        .login-card .link {
            color: #2563eb;
            text-decoration: underline;
            cursor: pointer;
            font-size: 13px;
        }
        .login-card .footer {
            margin-top: 1.25rem;
            font-size: 13px;
            color: #555;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<h2>🚀 Welcome to BitPanel</h2>", unsafe_allow_html=True)
    st.markdown("<p>Please log in to continue</p>", unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("🔐 Sign In", use_container_width=True):
        try:
            user = sign_in(email, password)
            user_id = user["localId"]
            token = user["idToken"]
            profile = load_user_profile(user_id, token) or {}
            account_info = profile.get("account", {})
            role = account_info.get("role", "lead")
            paid = account_info.get("paid", False)

            st.session_state.token = token
            st.session_state.role = role
            st.session_state.user = {
                "email": email,
                "token": token,
                "name": profile.get("name", "User"),
                "localId": user_id,
                "account": account_info,
                "role": role,
                "paid": paid
            }

            st.success("✅ Login successful!")
            st.session_state.page = "📊 Portfolio"
            st.session_state.current_page = "📊 Portfolio"
            st.rerun()

        except Exception as e:
            st.error("❌ Invalid email or password.")
            st.exception(e)

    # Forgot Password
    if st.markdown("<p class='link' style='text-align:right'>Forgot Password?</p>", unsafe_allow_html=True):
        st.session_state.page = "reset_password"
        st.rerun()

    # Sign Up
    st.markdown("""
        <div class='footer'>
            Need an account? <span class='link'>Sign up</span>
        </div>
    """, unsafe_allow_html=True)

    # Link triggers
    clicked_forgot = st.session_state.get("page") == "reset_password"
    clicked_signup = st.session_state.get("page") == "signup"

    if clicked_forgot:
        st.session_state.page = None
        st.session_state.current_page = "reset_password"
        st.rerun()
    elif clicked_signup:
        st.session_state.page = None
        st.session_state.current_page = "signup"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
