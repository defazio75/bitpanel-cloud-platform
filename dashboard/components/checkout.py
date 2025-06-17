import streamlit as st
import streamlit.components.v1 as components

def render_checkout(user_id):
    st.title("💳 Choose Your BitPanel Plan")

    user_info = st.session_state.user
    is_paid_user = user_info.get("paid", False)
    plan_code = user_info.get("plan", None)

    if is_paid_user:
        if plan_code == "pro_month":
            plan_name = "Pro – $24.99/mo"
        elif plan_code == "pro_annual":
            plan_name = "Pro Annual – $149.99/yr"
        else:
            plan_name = "Pro Plan"
    else:
        plan_name = "Free Version"

    st.markdown(f"**🔒 Current Plan:** `{plan_name}`")

    if is_paid_user:
        st.success("✅ You're already subscribed to the Pro version. Thanks for supporting BitPanel 🚀")
    else:
        st.warning("⚠️ You're currently on the Free Version. Upgrade to unlock live trading and more.")

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

    # === Pro Monthly Plan ===
    with col2:
        st.markdown("""
### 🚀 Pro Plan (Monthly)
~~$49.99~~ → **Now Only $24.99 / month**  
🔥 **Limited Time Offer!**  

- ✅ 30 Day Free Trial  
- ✅ Full Access to All Bot Strategies  
- ✅ Live + Paper Trading  
- ✅ Support for BTC, ETH, XRP, DOT, LINK, SOL  
- ✅ Connect with Coinbase, Binance, or Kraken  
- ✅ Cancel Anytime
        """)

        if st.button("👉 Subscribe Monthly"):
            components.html(
                """
                <script>
                window.open("https://buy.stripe.com/test_aFa6oA5oqgjcglk6OM5ZC01", "_blank");
                </script>
                """,
                height=0,
                width=0
            )

    # === Pro Annual Plan ===
    with col3:
        st.markdown("""
### 🎯 Pro Plan (Annual)
~~$299.99~~ → **Now Only $149.99 / year**  
🔥 **Limited Time Offer! (Save 50%)**  

- ✅ 30 Day Free Trial  
- ✅ 50% Annual Savings  
- ✅ Includes all Pro Plan Features  
- ✅ Cancel Anytime
        """)

        if st.button("👉 Subscribe Annually"):
            components.html(
                """
                <script>
                window.open("https://buy.stripe.com/test_00wdR27wy5Ey9WW0qo5ZC00", "_blank");
                </script>
                """,
                height=0,
                width=0
            )
