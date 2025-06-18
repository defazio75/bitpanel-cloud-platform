import streamlit as st
from utils.firebase_db import load_user_profile
from utils.firebase_auth import sign_in

def login():
    # Centered layout with limited width
    st.markdown(
        """
        <style>
        .login-card {
            max-width: 400px;
            margin: 5vh auto;
            padding: 2rem;
            background-color: #ffffff10;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .center-text {
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='center-text'>🔐 Welcome to BitPanel</h3>", unsafe_allow_html=True)
    st.markdown("<p class='center-text'>Please login to continue</p>", unsafe_allow_html=True)

    
    # Get user input
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In"):
            try:
                user = sign_in(email, password)
                user_id = user["localId"]
                token = user["idToken"]

                # Load profile from Firebase Realtime DB
                profile = load_user_profile(user_id, token) or {}
                account_info = profile.get("account", {})

                # Extract access data
                role = account_info.get("role", "lead")
                paid = account_info.get("paid", False)

                # Save to session state
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

                # Navigation
                st.success("✅ Login successful!")
                st.session_state.page = "📊 Portfolio"
                st.session_state.current_page = "📊 Portfolio"
                st.rerun()

            except Exception as e:
                st.error("❌ Invalid email or password. Try again.")
                st.exception(e)

    with col2:
        if st.button("Create Account"):
            st.session_state.page = "signup"
            st.rerun()

    # Forgot Password – centered below
    st.markdown("---")
    if st.button("🔁 Forgot Password?", use_container_width=True):
        st.session_state.reset_email = email
        st.session_state.page = "reset_password"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True) 
