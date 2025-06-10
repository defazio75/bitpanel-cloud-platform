import streamlit as st
from utils.firebase_db import save_live_snapshot_from_kraken, load_portfolio_snapshot
from utils.config import get_mode

def render_debug(user_id, token):
    mode = get_mode(user_id)

    st.title("🧪 Firebase Live Balance Test")
    st.write("📛 User ID:", user_id)
    st.write("🔄 Mode:", mode)

    if st.button("1️⃣ Save Live Snapshot to Firebase"):
        save_live_snapshot_from_kraken(user_id=user_id, token=token, mode=mode)

    if st.button("2️⃣ Load Snapshot from Firebase"):
        snapshot = load_portfolio_snapshot(user_id, token, mode)
        st.write("🧾 Snapshot from Firebase:", snapshot)
