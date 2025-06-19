import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # === Minimal Centered Styling ===
    st.markdown("""
        <style>
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {
            padding-top: 10vh;
            padding-bottom: 5vh;
            display: flex;
            justify-content: center;
        }
        .login-container {
            max-width: 400px;
            width: 100%;
            margin: auto;
        }
        .login-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("<h2 class='login-header'>🚀 Welcome to BitPanel</h2>", unsafe_allow_html=True)
    st.markdown("<p class='login-header'>Please login to continue</p>", unsafe_allow_html=True)

    # Inputs
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    # Buttons stacked
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
            st.error("❌ Invalid email or password. Try again.")
            st.exception(e)

    if st.button("🆕 Create Account", use_container_width=True):
        st.session_state.page = "signup"
        st.rerun()

    st.markdown("---")
    if st.button("🔁 Forgot Password?", use_container_width=True):
        st.session_state.reset_email = email
        st.session_state.page = "reset_password"
        st.rerun()
