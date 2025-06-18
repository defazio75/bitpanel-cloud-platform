import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    st.markdown("""
        <style>
        /* Background and layout */
        body {
            background-color: #f3f4f6;
        }

        #MainMenu, footer, header {visibility: hidden;}

        .block-container {
            padding-top: 12vh;
            display: flex;
            justify-content: center;
        }

        /* Login card style */
        .login-card {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .login-header {
            text-align: center;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 1.25rem;
        }

        .subtle-link {
            font-size: 13px;
            color: #2563eb;
            text-align: right;
            display: block;
            margin-top: -10px;
            margin-bottom: 1.5rem;
        }

        .bottom-text {
            text-align: center;
            font-size: 13px;
            margin-top: 1.5rem;
            color: #555;
        }

        .bottom-text a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    # Login UI
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='login-header'>🚀 Welcome to BitPanel</div>", unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    st.markdown("<a class='subtle-link' href='#'>Forgot your password?</a>", unsafe_allow_html=True)

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

    st.markdown("""
        <div class='bottom-text'>
            Need an account? <a href='#' onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'signup'}, '*')">Create one</a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
