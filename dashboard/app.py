import streamlit as st
st.set_page_config(page_title="BitPanel Dashboard", layout="wide")

import os
import sys
import json

from components.portfolio_summary import render_portfolio_summary
from components.coin_allocation import render as render_coin_allocation
from components.strategy import render as render_strategy_controls
from components.performance import render as render_performance
from components.current_positions import render as render_current_positions
from components.settings_panel import render_settings_panel
from utils.state_loader import load_bot_states
from config.config import get_mode, save_mode
from utils.paper_reset import reset_paper_account
from utils.kraken_wrapper import save_portfolio_snapshot
from utils.firebase_config import auth, firebase

def save_user_profile(user_id, name, email, token):
    db = firebase.database()
    db.child("users").child(user_id).set({
        "name": name,
        "email": email
    }, token)

def load_user_profile(user_id, token):
    db = firebase.database()
    return db.child("users").child(user_id).get(token).val()

def login():
    st.subheader("🔐 BitPanel Login")

    if "stage" not in st.session_state:
        st.session_state.stage = "email"
    if "email" not in st.session_state:
        st.session_state.email = ""

    # === STEP 1: Email Entry ===
    if st.session_state.stage == "email":
        email_input = st.text_input("Enter your email", key="email_input")

        if st.button("Continue") and email_input:
            st.session_state.email = email_input
            
            try:
                auth.sign_in_with_email_and_password(email_input, "__invalid_password__")
            except Exception as e:
                st.error("⚠️ Firebase error during email check.")
                st.code(str(e), language="bash")
                print("DEBUG: Firebase exception:", e)
                
                err_str = str(e)

                if "EMAIL_NOT_FOUND" in err_str:
                    st.session_state.stage = "signup"  # new user
                elif "INVALID_PASSWORD" in err_str:
                    st.session_state.stage = "login_or_signup"  # Existing user
                else:
                    st.session_state.stage = "email"

                st.rerun()

    # === STEP 2: Try Login ===
    elif st.session_state.stage == "login_or_signup":
        st.markdown(f"**Enter your password for {st.session_state.email}**")
        password = st.text_input("Password", type="password")

        if st.button("Log In"):
            try:
                user = auth.sign_in_with_email_and_password(st.session_state.email, password)
                user_id = user['localId']
                profile = load_user_profile(user_id, user['idToken'])

                st.session_state.user = {
                    "id": user_id,
                    "token": user['idToken'],
                    "email": user['email'],
                    "name": profile.get("name", "No Name") if profile else "No Name"
                }

                st.success("✅ Logged in successfully!")
                st.rerun()

            except Exception as e:
                err_str = str(e)
                if "EMAIL_NOT_FOUND" in err_str:
                    st.warning("📭 No account found. Please create one below.")
                    st.session_state.stage = "signup"
                elif "INVALID_PASSWORD" in err_str or "INVALID_LOGIN_CREDENTIALS" in err_str:
                    st.error("❌ Incorrect password.")
                else:
                    st.error(f"Unexpected login error: {err_str}")

    # === STEP 3: Create Account ===
    elif st.session_state.stage == "signup":
        st.markdown(f"**Create a new account for {st.session_state.email}**")
        name = st.text_input("Full Name")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if password != confirm_password:
                st.error("❌ Passwords do not match.")
            elif not name:
                st.error("❌ Name is required.")
            else:
                try:
                    user = auth.create_user_with_email_and_password(st.session_state.email, password)
                    user_id = user['localId']
                    save_user_profile(user_id, name, st.session_state.email, user['idToken'])
                    st.session_state.user = {
                        "id": user_id,
                        "token": user['idToken'],
                        "email": st.session_state.email,
                        "name": name
                    }
                    st.success("✅ Account created and logged in!")
                    st.rerun()
                except Exception as e:
                    if "EMAIL_EXISTS" in str(e):
                        st.error("❌ Email already in use. Try logging in instead.")
                        st.session_state.stage = "login_or_signup"
                    else:
                        st.error(f"Signup failed: {e}")

if "user" not in st.session_state or "id" not in st.session_state.user:
    login()
    st.stop()
 
user_id = st.session_state.user['id']
api_key_path = f"config/{user_id}/kraken_keys.json"
api_key_exists = os.path.exists(api_key_path)

# === Sync session_state with mode.json on load ===
current_mode = get_mode()
if "mode" not in st.session_state:
    st.session_state.mode = current_mode
if "pending_mode" not in st.session_state:
    st.session_state.pending_mode = st.session_state.mode
if "show_mode_confirm" not in st.session_state:
    st.session_state.show_mode_confirm = False

mode = st.session_state.mode

# === LIVE MODE BLOCKER ===
if mode == "live" and not os.path.exists(api_key_path):
    st.error("⚠️ API keys are required to activate live trading mode.")

    with st.form("api_key_form_live"):
        new_key = st.text_input("Kraken API Key")
        new_secret = st.text_input("Kraken API Secret", type="password")
        submit = st.form_submit_button("Save API Keys")

    if submit and new_key and new_secret:
        os.makedirs(os.path.dirname(api_key_path), exist_ok=True)
        with open(api_key_path, "w") as f:
            json.dump({"api_key": new_key, "api_secret": new_secret}, f)
        st.success("✅ API keys saved. You can now use Live mode.")
        st.rerun()

# Initialize current page
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "📊 Portfolio"

# Save snapshot if in live mode
if st.session_state.mode == "live":
    save_portfolio_snapshot("live")

# === Handle Mode Change Prompt ===
def request_mode_change(new_mode):
    if new_mode != st.session_state.mode:
        st.session_state.pending_mode = new_mode
        st.session_state.show_mode_confirm = True

# === Apply Color Tint to Sidebar ===
sidebar_color = "#fff8dc" if st.session_state.mode == "paper" else "#e6ffe6"

st.markdown(
    f"""
    <style>
        section[data-testid="stSidebar"] {{
            background-color: {sidebar_color};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("### ⚙️ Mode")

    # Show logged-in user
    if "user" in st.session_state:
        st.markdown(f"👤 Logged in as: **{st.session_state.user['name']}**")

    mode_labels = {"paper": "Paper Trading", "live": "Live Trading"}
    reverse_labels = {v: k for k, v in mode_labels.items()}

    selected_label = st.radio(
        "Select Mode",
        list(mode_labels.values()),
        index=0 if st.session_state.mode == "paper" else 1,
        key="mode_selector"
    )

    selected_mode = reverse_labels[selected_label]

    if selected_mode != st.session_state.mode:
        st.session_state.pending_mode = selected_mode
        st.session_state.show_mode_confirm = True

    if st.session_state.show_mode_confirm:
        st.warning(f"Change to {st.session_state.pending_mode}?")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Confirm"):
                st.session_state.mode = st.session_state.pending_mode
                save_mode(st.session_state.mode)
                st.session_state.show_mode_confirm = False
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.show_mode_confirm = False
                st.session_state.mode_selector = st.session_state.mode  # revert radio button

    if st.session_state.mode == "paper":
        st.markdown("### 🔄 Reset Paper Account")

        if "show_reset_confirm" not in st.session_state:
            st.session_state.show_reset_confirm = False

        if not st.session_state.show_reset_confirm:
            if st.button("⚠️ Reset Paper Account"):
                st.session_state.show_reset_confirm = True
        else:
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✅ Confirm Reset", key="confirm_reset_btn"):
                    reset_paper_account()
                    st.success("Paper account reset successfully.")
                    st.session_state.show_reset_confirm = False
            with col2:
                if st.button("❌ Cancel", key="cancel_reset_btn"):
                    st.session_state.show_reset_confirm = False

    # === Navigation ===
    st.markdown("- - -")
    st.markdown("""
        <style>
        .sidebar-bubble {
            padding: 12px 20px;
            margin-bottom: 10px;
            border-radius: 25px;
            background-color: #f1f3f8;
            font-weight: bold;
            font-size: 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .sidebar-bubble:hover {
            background-color: #3475e1;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    pages = [
        "📊 Portfolio",
        "💰 Allocation",
        "🧠 Strategies",
        "📜 Positions",
        "📈 Performance",
        "⚙️ Settings"
    ]

    for page in pages:
        if st.button(page, key=f"nav_{page}"):
            st.session_state["current_page"] = page

# === Main Content Area ===
st.title("🚀 BitPanel")

if st.button("🔓 Log Out"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("You have been logged out.")
    st.rerun()

current_page = st.session_state["current_page"]
mode = st.session_state.mode

if current_page == "📊 Portfolio":
    render_portfolio_summary(mode=mode)

elif current_page == "💰 Allocation":
    bot_states = load_bot_states()
    render_coin_allocation(mode=mode) 

elif current_page == "🧠 Strategies":
    render_strategy_controls(mode=mode)

elif current_page == "📜 Positions":
    render_current_positions(mode=mode)

elif current_page == "📈 Performance":
    render_performance()

elif current_page == "⚙️ Settings":
    render_settings_panel()

    if not os.path.exists(api_key_path):
        st.warning("⚠️ API Keys not found. Please enter your Kraken API credentials to activate BitPanel.")

        with st.form("api_key_form"):
            new_key = st.text_input("Kraken API Key")
            new_secret = st.text_input("Kraken API Secret", type="password")
            submit = st.form_submit_button("Save API Keys")

        if submit and new_key and new_secret:
            os.makedirs(os.path.dirname(api_key_path), exist_ok=True)
            with open(api_key_path, "w") as f:
                json.dump({"api_key": new_key, "api_secret": new_secret}, f)
            st.success("✅ API keys saved. You're ready to go!")
            st.rerun()
