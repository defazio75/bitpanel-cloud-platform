import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# === Section 1: Total Portfolio Performance (Mock Data) ===
st.header("📈 Total Portfolio Performance")

timeframes = ["Daily", "Weekly", "Monthly", "Yearly"]
portfolio_returns = [1.2, 4.8, 12.5, 56.7]  # mock % returns
hodl_returns = [0.8, 3.5, 10.2, 50.3]       # mock % returns

df_total = pd.DataFrame({
    "Timeframe": timeframes,
    "BitPanel": portfolio_returns,
    "HODL": hodl_returns
})

st.subheader("BitPanel vs HODL")
fig1, ax1 = plt.subplots()
df_total.set_index("Timeframe").plot(kind="bar", ax=ax1)
ax1.set_ylabel("Return (%)")
ax1.set_title("BitPanel vs HODL Performance")
st.pyplot(fig1)

# === Section 2: Individual Coin Performance (Mock Data) ===
st.header("📊 Individual Coin Performance")

coins = ["BTC", "ETH", "XRP", "DOT"]
bitpanel_returns = [15.3, 22.7, 8.1, 10.4]
market_returns = [10.1, 18.5, 6.0, 7.8]

df_coin = pd.DataFrame({
    "Coin": coins,
    "BitPanel": bitpanel_returns,
    "Market": market_returns
})

st.subheader("BitPanel ROI vs Coin Performance")
fig2, ax2 = plt.subplots()
df_coin.set_index("Coin").plot(kind="bar", ax=ax2)
ax2.set_ylabel("Return (%)")
ax2.set_title("Per-Coin Return Comparison")
st.pyplot(fig2)

# === Section 3: Coin Stacking Progress (Mock Data) ===
st.header("🪙 Coin Stacking Progress")

stacking_data = {
    "BTC": 0.0352,
    "ETH": 0.6741,
    "XRP": 201.23,
    "DOT": 13.98
}

df_stack = pd.DataFrame(list(stacking_data.items()), columns=["Coin", "Coins Gained"])
st.dataframe(df_stack)

# === Section 4: Placeholder ===
st.header("📦 Fourth Performance Metric (TBD)")
st.info("This section is reserved for another performance insight. Let's define it next.")
