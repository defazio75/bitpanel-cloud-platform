import streamlit as st
import time
import os
import sys

st.set_page_config(page_title="BitPanel Dashboard", layout="wide")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from components.portfolio_summary import render_portfolio_summary
from components.coin_allocation import render_coin_allocation
from components.strategy import render_strategy_controls
from components.performance import render_performance
from components.current_positions import render_current_positions
from components.settings_panel import render_settings_panel
from components.login import login
from components.signup import signup
from components.reset_password import reset_password
from components.checkout import render_checkout
from utils.paper_reset import reset_paper_account
from utils.load_keys import load_user_api_keys, api_keys_exist

# === Page Router ===
def run():
    page = st.session_state.get("current_page", "login")

    if page == "login":
        login()
    elif page == "signup":
        signup()
    elif page == "reset_password":
        reset_password()
    else:
        login()

# === PROTECTED AREA (Requires Logged-in User) ===
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.session_state.page = "login"
    st.rerun()

# === Determine initial mode based on API keys ===
user_id = st.session_state.user["localId"]
st.session_state.role = st.session_state.user.get("role", "lead")
token = st.session_state.token
exchange = "kraken"

if "api_keys" not in st.session_state:
    st.session_state.api_keys = load_user_api_keys(user_id, exchange, token=token)

user_api_keys = st.session_state.api_keys

if "mode" not in st.session_state:
    role = st.session_state.user.get("role", "lead")
    if user_api_keys and user_api_keys.get("key") and user_api_keys.get("secret") and role in ["admin", "customer"]:
        st.session_state.mode = "live"
    else:
        st.session_state.mode = "paper"

mode = st.session_state.mode

REFRESH_INTERVAL = 10  # seconds

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    st.session_state.last_refresh = time.time()
    st.rerun()

# === GATEKEEP LIVE MODE ACCESS ===
if st.session_state.mode == "live":
    if not api_keys_exist(user_id, token, exchange="kraken"):
        st.warning("🔐 Live mode requires saved API keys. Switching back to Paper mode.")
        st.session_state.mode = "paper"
        st.rerun()
    else:
        role = st.session_state.role
        if role not in ["admin", "customer"]:
            st.warning("💳 Live mode is only available for active users. Switching to Paper mode.")
            st.session_state.mode = "paper"
            st.rerun()

# Initialize current page
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "📊 Portfolio"

# === Handle Mode Change Prompt ===
def request_mode_change(new_mode):
    if new_mode != st.session_state.mode:
        st.session_state.pending_mode = new_mode
        st.session_state.show_mode_confirm = True

# === Apply Color Tint to Sidebar ===
sidebar_color = "#f4f4f4" if st.session_state.mode == "paper" else "#e6ffe6"

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
    st.title("🚀 BitPanel")
    st.markdown(f"👤 Logged in as: **{st.session_state.user.get('name', 'User')}**")

    if st.button("🔓 Log Out", help="End your session and return to login"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
        st.rerun()

    account = st.session_state.user
    if account.get("paid", False) or account.get("bypass", False):
        st.success("✅ Pro Plan Active")
    elif account.get("bypass", False):
        st.success("✅ Dev Access (Bypass)")
    else:
        st.info("💡 Live trading requires a Pro subscription")
        if st.button("🚀 Upgrade to Pro", key="upgrade_button_sidebar"):
            st.session_state.current_page = "checkout"
            st.rerun()

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
        if selected_mode == "live":
            st.session_state.api_keys = load_user_api_keys(user_id, exchange, token=token)
            
            # 🚫 Check API keys
            has_keys = st.session_state.api_keys and st.session_state.api_keys.get("key") and st.session_state.api_keys.get("secret")

            # 🚫 Check subscription status (from session_state or Firebase in future)
            role = st.session_state.role
            has_access = role in ["admin", "customer"]

            if not has_keys:
                st.warning("⚠️ Live mode requires saved API keys.")
                if st.button("🔧 Go to API Settings", key="api_key_redirect_button"):
                    st.session_state.current_page = "⚙️ Settings"
                    st.rerun()
            elif not has_access:
                st.error("💳 Upgrade to BitPanel Pro for Live trading")
                if st.button("🚀 Subscribe Now", key="upgrade_button_live_warning"):
                    st.session_state.current_page = "checkout"
                    st.rerun()
            else:
                request_mode_change(selected_mode)
        else:
            request_mode_change(selected_mode)

    if "show_mode_confirm" not in st.session_state:
        st.session_state.show_mode_confirm = False

    if st.session_state.show_mode_confirm:
        st.warning(f"Change to {st.session_state.pending_mode}?")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Confirm", key="confirm_mode_change"):
                st.session_state.mode = st.session_state.pending_mode
                st.session_state.show_mode_confirm = False
                st.rerun()
        with col2:
            if st.button("❌ Cancel", key="cancel_mode_change"):
                st.session_state.show_mode_confirm = False
                st.session_state.mode_selector = st.session_state.mode

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
                    reset_paper_account(user_id)
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
current_page = st.session_state["current_page"]
mode = st.session_state.mode

if current_page == "📊 Portfolio":
    render_portfolio_summary(mode=mode, user_id=user_id, token=token)

elif current_page == "💰 Allocation":
    render_coin_allocation(mode=mode, user_id=user_id, token=token)

elif current_page == "🧠 Strategies":
    render_strategy_controls(mode=mode, user_id=user_id, token=token)

elif current_page == "📜 Positions":
    render_current_positions(mode=mode, user_id=user_id, token=token)

elif current_page == "📈 Performance":
    render_performance(mode=mode, user_id=user_id, token=token)

elif current_page == "⚙️ Settings":
    render_settings_panel(user_id=user_id, exchange=exchange, token=token)

elif current_page == "checkout":
    render_checkout(user_id=user_id)
