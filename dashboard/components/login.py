import streamlit as st

def login():
    # === Styling ===
    st.markdown("""
        <style>
        [data-testid="stAppViewContainer"] > .main {
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f5f5f5;
        }
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
            font-size: 13px;
            cursor: pointer;
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

    # === Layout Start ===
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<h3>🚀 Welcome to BitPanel</h3>", unsafe_allow_html=True)
    st.markdown("<p>Please log in to continue</p>", unsafe_allow_html=True)

    st.text_input("Email", key="login_email")
    st.text_input("Password", type="password", key="login_password")

    # Static blue link for now (no click action yet)
    st.markdown("""
        <div class='forgot-wrapper'>
            <span class='forgot-link'>Forgot Password?</span>
        </div>
    """, unsafe_allow_html=True)

    st.button("🔐 Sign In", use_container_width=True)

    st.markdown("""
        <div class='signup-wrapper'>
            Need an account? <span class='signup-link'>Sign up</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
