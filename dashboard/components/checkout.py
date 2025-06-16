import streamlit as st
import webbrowser

def render_checkout(user_id):
    st.title("💳 Choose Your BitPanel Plan")

    is_paid_user = st.session_state.user.get("paid", False)
    plan_name = st.session_state.user.get("plan_name", "Free Version" if not is_paid_user else "Pro Plan")

    st.markdown(f"**🔒 Current Plan:** `{plan_name}`")
    if is_paid_user:
        st.success("You're already subscribed to the Pro version. Thanks for supporting BitPanel 🚀")
    else:
        st.warning("You're currently on the Free Version. Upgrade to unlock live trading and more.")

    st.markdown("---")

    # === Pricing Layout ===
    col1, col2, col3 = st.columns(3)

    # === Free Plan ===
    with col1:
        st.markdown("### 🧪 Free Version")
        st.markdown("""
        - Paper Trading Only  
        - Full Dashboard Access  
        - Strategy Allocation Controls  
        - Portfolio Tracking (Simulated)  
        """)
        st.button("✅ You're on this plan", disabled=True)

    # === Pro Monthly ===
    with col2:
        st.markdown("### 🚀 Pro Plan (Monthly)")
        st.markdown("""
        **$24.99 / month**  
        - ✅ Live Trading  
        - ✅ Real Exchange Execution  
        - ✅ Priority Feature Access  
        - ✅ Email Support  
        """)
        if st.button("📅 Subscribe Monthly"):
            webbrowser.open_new_tab("https://buy.stripe.com/test_aFa6oA5oqgjcglk6OM5ZC01")

    # === Pro Annual ===
    with col3:
        st.markdown("### 💼 Pro Plan (Annual)")
        st.markdown("""
        **$149.99 / year** *(Save 50%)*  
        - ✅ Everything in Monthly  
        - ✅ Priority Support  
        - ✅ Early Feature Access  
        """)
        if st.button("📆 Subscribe Annually"):
            webbrowser.open_new_tab("https://buy.stripe.com/test_00wdR27wy5Ey9WW0qo5ZC00")
