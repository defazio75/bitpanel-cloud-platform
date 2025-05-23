# /dashboard/components/trade_log.py

import streamlit as st
import pandas as pd
from utils.state_loader import load_trade_log

def render_trade_log():
    st.header("📋 Trade Log")

    # Load the trade log list
    trade_log = load_trade_log()

    if not trade_log:
        st.info("No trades recorded yet.")
        return

    # Convert list to DataFrame
    trade_log_df = pd.DataFrame(trade_log)

    # If no rows even after conversion
    if trade_log_df.empty:
        st.info("No trades recorded yet.")
        return

    # Sort trades by most recent
    trade_log_df = trade_log_df.sort_values(by="timestamp", ascending=False)

    # Only show the last 5 trades for now
    recent_trades = trade_log_df.head(5)

    # Display as a table
    st.dataframe(
        recent_trades[['timestamp', 'coin', 'strategy', 'action', 'amount', 'price', 'profit']],
        use_container_width=True
    )