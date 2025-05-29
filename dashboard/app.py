import streamlit as st
st.set_page_config(page_title="BitPanel Dashboard", layout="wide")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=600_000, limit=None, key="keepalive")

import os
import sys
import json

from components.portfolio_summary import render_portfolio_summary
from components.coin_allocation import render as render_coin_allocation
from components.strategy import render as render_strategy_controls
from components.performance import render as render_performance
from components.current_positions import render as render_current_positions
from components.settings_panel import render_settings_panel
from components.login import login
from components.signup import signup
from components.reset_password import reset_password
from utils.state_loader import load_bot_states
from config.config import get_mode, save_mode
from utils.paper_reset import reset_paper_account
from utils.kraken_wrapper import save_portfolio_snapshot
from utils.load_keys import load_api_keys

if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    login()
    st.stop()
elif st.session_state.page == "signup":
    signup()
    st.stop()
elif st.session_state.page == "reset_password":
    reset_password()
    st.stop()

# === PROTECTED AREA (Requires Logged-in User) ===
if "user" not in st.session_state:
    st.warning("Please log in first.")
    st.session_state.page = "login"
    st.rerun()
 
user_id = st.session_state.user["id"]
exchange = "kraken"  # Default for now
keys = load_api_keys()

# === Sync session_state with mode.json on load ===
current_mode = get_mode()
if "mode" not in st.session_state:
    st.session_state.mode = current_mode
if "pending_mode" not in st.session_state:
    st.session_state.pending_mode = st.session_state.mode
if "show_mode_confirm" not in st.session_state:
    st.session_state.show_mode_confirm = False

mode = st.session_state.mode

# === GATEKEEP LIVE MODE ACCESS ===
if mode == "live":
    if not keys:
        st.warning("🔐 Live mode requires API keys. You've been switched back to Paper mode.")
        st.session_state.mode = "paper"
        save_mode("paper")
        st.rerun()
    # (In the future) Also check for paid user status here

# === Save snapshot if in live mode ===
if st.session_state.mode == "live":
    save_portfolio_snapshot("live")

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

    # Show logged-in user
    if "user" in st.session_state:
        st.markdown(f"👤 Logged in as: **{st.session_state.user.get('name', 'User')}**")

        # === Log Out Button at Top ===
    if st.button("🔓 Log Out", help="End your session and return to login"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("You have been logged out.")
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
        if selected_mode == "live" and not keys:
            st.warning("⚠️ Live mode requires saved API keys.")
            if st.button("🔧 Go to API Settings"):
                st.session_state.current_page = "⚙️ Settings"
                st.rerun()        
        else:
            request_mode_change(selected_mode)

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
st.title("🚀 BitPanel")

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
    render_settings_panel(user_id=user_id, exchange=exchange)
