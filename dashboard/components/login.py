import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # 🔧 Remove ghost top div
    st.markdown("""
        <style>
        .block-container > div:first-child:empty {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    # === Styling ===
    st.markdown("""
        <style>
        #MainMenu, header, footer {visibility: hidden;}
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
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            text-align: center;
        }
        .login-header {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .forgot-link, .signup-link {
            color: #2563eb;
            text-decoration: underline;
            cursor: pointer;
            font-size: 13px;
            display: inline-block;
        }
        .forgot-wrapper {
            text-align: right;
            margin-top: -10px;
            margin-bottom: 20px;
        }
        .signup-wrapper {
            text-align: center;
            font-size: 13px;
            margin-top: 20px;
            color: #555;
        }
        </style>
    """, unsafe_allow_html=True)

    # === Layout ===
    st.markdown("<div class='login-wrapper'><div class='login-card'>", unsafe_allow_html=True)

    st.markdown("""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <h3 style='margin-bottom: 0.25rem;'>🚀 Welcome to BitPanel</h3>
        </div>
    """, unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    # Forgot Password link (styled + triggers routing below)
    st.markdown("<div class='forgot-wrapper'><span class='forgot-link'>Forgot Password?</span></div>", unsafe_allow_html=True)

    # Sign In button
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

    # Sign up link
    st.markdown("""
        <div class='signup-wrapper'>
            Need an account?
            <span class='signup-link'> Sign up</span>
        </div>
    """, unsafe_allow_html=True)

    # Check for link clicks using a clever hack with JavaScript injection
    st.markdown("""
        <script>
        const forgot = window.parent.document.querySelector('span.forgot-link');
        if (forgot) {
            forgot.onclick = () => {
                window.parent.postMessage({type: 'streamlit:rerun', page: 'reset_password'}, '*');
            };
        }
        const signup = window.parent.document.querySelector('span.signup-link');
        if (signup) {
            signup.onclick = () => {
                window.parent.postMessage({type: 'streamlit:rerun', page: 'signup'}, '*');
            };
        }
        </script>
    """, unsafe_allow_html=True)

    # Fallback: if routing fails, use buttons as invisible triggers
    if "page" in st.session_state:
        if st.session_state.page == "reset_password":
            st.session_state.page = None
            st.session_state.current_page = "reset_password"
            st.rerun()
        elif st.session_state.page == "signup":
            st.session_state.page = None
            st.session_state.current_page = "signup"
            st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)
