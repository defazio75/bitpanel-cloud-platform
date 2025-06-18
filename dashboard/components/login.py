import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # Inject styling to control layout + card width
    st.markdown("""
        <style>
        /* Hide unnecessary elements */
        #MainMenu, footer, header {visibility: hidden;}

        /* Lock main container layout */
        .block-container {
            padding-top: 12vh;
            display: flex;
            justify-content: center;
        }

        /* Outer wrapper for the card */
        .login-wrapper {
            width: 100%;
            max-width: 420px;
        }

        /* Login card bubble */
        .login-card {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .login-header {
            text-align: center;
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 1rem;
        }

        .subtle-link {
            font-size: 13px;
            color: #2563eb;
            text-align: right;
            display: block;
            margin-top: -10px;
            margin-bottom: 20px;
        }

        .bottom-text {
            text-align: center;
            font-size: 13px;
            margin-top: 20px;
            color: #555;
        }

        .bottom-text a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 500;
        }

        .block-container > div:first-child:empty {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # ✅ Start outer wrapper to restrict width
    st.markdown("<div class='login-wrapper'><div class='login-card'>", unsafe_allow_html=True)
    
    # --- Inside the bubble ---
    st.markdown("<div class='login-header'>🚀 BitPanel Login</div>", unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("🔁 Forgot your password?", key="forgot_pw_link"):
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

    st.markdown("<div class='bottom-text'>Need an account?</div>", unsafe_allow_html=True)
    if st.button("🆕 Create one", key="create_account_link"):
        st.session_state.page = "signup"
        st.rerun()

    # End bubble
    st.markdown("</div>", unsafe_allow_html=True)
