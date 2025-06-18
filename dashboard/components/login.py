import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # === Styling for layout and card ===
    st.markdown("""
        <style>
        /* Hide extra UI elements */
        #MainMenu, footer, header {visibility: hidden;}
        .block-container {
            padding-top: 12vh;
            display: flex;
            justify-content: center;
        }
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
        .signup-text {
            font-size: 13px;
            color: #555;
            margin-top: 20px;
        }
        .signup-text a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # === Start Login Card ===
    st.markdown("<div class='login-wrapper'><div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<div class='login-header'>🚀 Welcome to BitPanel</div>", unsafe_allow_html=True)
    st.markdown("Please log in to continue")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    # 🔵 Forgot Password link — styled like a hyperlink but functional
    col_forgot, _ = st.columns([1, 5])
    with col_forgot:
        if st.button("Forgot Password?", key="forgot_pw", help="Reset your password"):
            st.session_state.page = "reset_password"
            st.rerun()

    st.markdown("""
        <style>
        button[kind="secondary"][data-testid="baseButton-forgot_pw"] {
            background: none;
            color: #2563eb;
            border: none;
            padding: 0;
            font-size: 13px;
            text-decoration: underline;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # 🔐 Sign In
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

    # 🔵 Sign Up link under the card
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<div class='signup-text'>Need an account?</div>", unsafe_allow_html=True)
    with col2:
        if st.button("Sign up", key="signup_link", help="Create a new BitPanel account"):
            st.session_state.page = "signup"
            st.rerun()

    # Style Sign up as a link
    st.markdown("""
        <style>
        button[kind="secondary"][data-testid="baseButton-signup_link"] {
            background: none;
            color: #2563eb;
            border: none;
            padding: 0;
            font-size: 13px;
            text-decoration: underline;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # === End login card ===
    st.markdown("</div></div>", unsafe_allow_html=True)
