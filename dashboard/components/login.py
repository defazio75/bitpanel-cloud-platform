import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # === Styling for layout and card ===
    st.markdown("""
        <style>
        /* Hide Streamlit built-in elements */
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
            margin-bottom: 1rem;
        }

        .forgot-password, .signup-link {
            font-size: 13px;
            color: #2563eb;
            text-decoration: none;
            cursor: pointer;
            display: inline-block;
            margin-top: 10px;
        }

        .signup-wrapper {
            margin-top: 20px;
            font-size: 13px;
            color: #555;
        }

        .signup-wrapper a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
            cursor: pointer;
        }

        .block-container > div:first-child:empty {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # === Start Card Layout ===
    st.markdown("<div class='login-wrapper'><div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<div class='login-header'>🚀 Welcome to BitPanel</div>", unsafe_allow_html=True)
    st.markdown("<p>Please log in to continue</p>", unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    # Forgot Password link (looks like text but works like a route)
    if st.markdown("<span class='forgot-password'>Forgot Password?</span>", unsafe_allow_html=True):
        pass  # Pure styling only — click handling below

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

    # Manual clickable links below
    if st.button("🔁 Reset Password", key="reset_pw_link", help="Click here to reset your password"):
        st.session_state.page = "reset_password"
        st.rerun()

    st.markdown("""
        <div class='signup-wrapper'>
            Need an account? <a href='#' id='signup-link'>Sign up</a>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🆕 Go to Signup", key="signup_link"):
        st.session_state.page = "signup"
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
