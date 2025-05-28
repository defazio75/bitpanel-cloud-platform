import streamlit as st
from utils.firebase_auth import send_password_reset

def reset_password():
    st.title("🔑 Reset Your Password")
    st.markdown("Enter your email below to receive a reset link.")

    default_email = st.session_state.get("reset_email", "")
    email = st.text_input("Email", value=default_email, key="reset_email_input")

    if st.button("📬 Send Reset Email"):
        try:
            send_password_reset(email)
            st.success(f"✅ A reset link has been sent to **{email}**.")
        except Exception as e:
            st.error("❌ Failed to send reset email.")
            st.exception(e)  # optional: show full error during dev

    if st.button("⬅️ Back to Login"):
        st.session_state.page = "login"
        st.experimental_rerun()
