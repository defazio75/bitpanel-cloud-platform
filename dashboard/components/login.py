import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # === Login Card Start ===
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<h3>🚀 Welcome to BitPanel</h3>", unsafe_allow_html=True)
    st.markdown("<p>Please log in to continue</p>", unsafe_allow_html=True)

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    st.markdown("""
        <div class='forgot-wrapper'>
            <span class='forgot-link'>Forgot Password?</span>
        </div>
    """, unsafe_allow_html=True)

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
        <div class='signup-wrapper'>
            Need an account? <span class='signup-link'>Sign up</span>
        </div>
    """, unsafe_allow_html=True)

    # Close login card
    st.markdown("</div>", unsafe_allow_html=True)

    # === Link click logic ===
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

    if "page" in st.session_state:
        if st.session_state.page == "reset_password":
            st.session_state.page = None
            st.session_state.current_page = "reset_password"
            st.rerun()
        elif st.session_state.page == "signup":
            st.session_state.page = None
            st.session_state.current_page = "signup"
            st.rerun()
