import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # === Fullscreen CSS layout & card style ===
    st.markdown("""
        <style>
        /* Force full-height layout and background */
        [data-testid="stAppViewContainer"] > .main {
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f5f5f5;
        }

        /* Centered login card */
        .login-card {
            width: 100%;
            max-width: 400px;
            background-color: #fff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            text-align: center;
        }

        .login-card h3 {
            margin-bottom: 0.25rem;
            font-size: 24px;
        }

        .login-card p {
            margin-top: 0;
            margin-bottom: 1.5rem;
            font-size: 14px;
            color: #666;
        }

        .forgot-link, .signup-link {
            color: #2563eb;
            text-decoration: underline;
            cursor: pointer;
            font-size: 13px;
        }

        .forgot-wrapper {
            text-align: right;
            margin-top: -10px;
            margin-bottom: 20px;
        }

        .signup-wrapper {
            text-align: center;
            margin-top: 20px;
            font-size: 13px;
            color: #555;
        }
        </style>
    """, unsafe_allow_html=True)

    # === Start Layout ===
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    # Title + Subtitle
    st.markdown("<h3>🚀 Welcome to BitPanel</h3>", unsafe_allow_html=True)
    st.markdown("<p>Please log in to continue</p>", unsafe_allow_html=True)

    # Form Inputs
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    # Forgot Password
    st.markdown("""
        <div class='forgot-wrapper'>
            <span class='forgot-link'>Forgot Password?</span>
        </div>
    """, unsafe_allow_html=True)

    # Sign In Button
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

    # Sign Up Link
    st.markdown("""
        <div class='signup-wrapper'>
            Need an account? <span class='signup-link'>Sign up</span>
        </div>
    """, unsafe_allow_html=True)

    # === End Layout ===
    st.markdown("</div>", unsafe_allow_html=True)

    # === JS link handlers ===
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

    # === Fallback if JS fails ===
    if "page" in st.session_state:
        if st.session_state.page == "reset_password":
            st.session_state.page = None
            st.session_state.current_page = "reset_password"
            st.rerun()
        elif st.session_state.page == "signup":
            st.session_state.page = None
            st.session_state.current_page = "signup"
            st.rerun()
