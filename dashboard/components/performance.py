import streamlit as st

def render_performance():
    st.title("📈 Performance Dashboard")

    # Section 1: Total Portfolio Performance
    st.subheader("Total Portfolio Performance")
    st.metric("Daily", "+2.5%")
    st.metric("Weekly", "+6.8%")
    st.metric("Monthly", "+15.2%")
    st.metric("Yearly", "+103.4%")

    st.markdown("---")

    # Section 2: Individual Coin Performance
    st.subheader("Individual Coin Performance")
    st.write("BTC: +3.1% daily, +12.4% monthly")
    st.write("ETH: +1.7% daily, +9.3% monthly")
    st.write("XRP: -0.5% daily, +4.8% monthly")

    st.markdown("---")

    # Section 3: Coin Stacking Progress
    st.subheader("Coin Stacking Progress")
    st.write("BTC: +0.024 accumulated")
    st.write("ETH: +0.61 accumulated")
    st.write("XRP: +130.4 accumulated")

    st.markdown("---")

    # Placeholder for Section 4
    st.subheader("Coming Soon: Strategy Performance vs HODL")
    st.info("This section will compare strategy performance against passive HODL performance.")
