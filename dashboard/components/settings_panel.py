# /dashboard/components/settings_panel.py

import streamlit as st

def render_settings_panel():
    st.header("⚙️ Settings Panel")

    st.subheader("🔄 Auto-Refresh Settings")
    refresh_enabled = st.toggle("Enable Auto-Refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", min_value=5, max_value=300, value=60, step=5)

    st.subheader("🛠 Future Settings (Coming Soon)")
    st.info("API Key management, bot threshold tuning, and notifications will be added here.")

    # Save the settings in Streamlit session_state (temporary storage)
    st.session_state['refresh_enabled'] = refresh_enabled
    st.session_state['refresh_interval'] = refresh_interval
