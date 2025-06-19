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

    # === Styled Links ===
    st.markdown("""
        <div class='forgot-wrapper'>
            <a href='?page=reset_password' style='color:#1E90FF; text-decoration:underline;'>Forgot Password?</a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='signup-wrapper'>
            Need an account? <a href='?page=signup' style='color:#1E90FF; text-decoration:underline;'>Sign up</a>
        </div>
    """, unsafe_allow_html=True)

    # === Check query param for navigation ===
    query_params = st.query_params
    page_param = query_params.get("page", [None])[0]

    if page_param == "reset_password":
        st.session_state.page = "reset_password"
        st.session_state.current_page = "reset_password"
        st.rerun()

    elif page_param == "signup":
        st.session_state.page = "signup"
        st.session_state.current_page = "signup"
        st.rerun()

    # Close login card
    st.markdown("</div>", unsafe_allow_html=True)
