import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # === Styling: Clean, centered 6x4 card layout ===
    st.markdown("""
        <style>
        /* Hide Streamlit fluff */
        #MainMenu, footer, header {visibility: hidden;}

        /* Center layout */
        .block-container {
            padding-top: 12vh;
            display: flex;
            justify-content: center;
        }

        /* Login card container */
        .login-wrapper {
            width: 100%;
            max-width: 400px;
        }

        .login-card {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            text-align: center;
        }

        .login-header {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .link-inline {
            font-size: 13px;
            margin-top: 0.75rem;
        }

        .link-inline a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }

        .forgot-link {
            text-align: right;
            font-size: 13px;
            margin-top: -10px;
            margin-bottom: 1.25rem;
        }

        .forgot-link a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }

        /* Optional fix for ghost block */
        .block-container > div:first-child:empty {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # === Start outer wrapper ===
    st.markdown("<div class='login-wrapper'><div class='login-card'>", unsafe_allow_html=True)

    # --- Login content ---
    st.markdown("<div class='login-header'>🚀 Welcome to BitPanel</div>", unsafe_allow_html=True)
    st.markdown("<p>Please log in to continue</p>", unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    # Forgot password link
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("🔁 Forgot Password?", key="forgot_pw"):
            st.session_state.page = "reset_password"
            st.rerun()

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

    # --- Bottom: "Need an account? Sign up" ---
    st.markdown("<div class='link-inline'>Need an account? <a href='#' onclick='document.dispatchEvent(new CustomEvent(\"signup\"))'>Sign up</a></div>", unsafe_allow_html=True)

    # Manual routing fallback for "Sign up" (button version)
    if st.button("🆕 Sign Up", key="signup_route_button"):
        st.session_state.page = "signup"
        st.rerun()

    # === End card ===
    st.markdown("</div></div>", unsafe_allow_html=True)
