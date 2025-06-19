import streamlit as st
import streamlit.components.v1 as components

def render_checkout(user_id):
    st.title("💳 Choose Your Plan")

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
        st.markdown("### 🚀 Monthly Pro Plan")
        st.markdown(
            "<p><span style='text-decoration: line-through;'>$49.99</span> &nbsp; <strong>Now Only $24.99!</strong></p>",
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
    🔥 **Limited Time Offer! (Save 50%)**

    - ✅ 30 Day Free Trial  
    - ✅ Full Access to All Bot Strategies  
    - ✅ Live + Paper Trading  
    - ✅ Support for BTC, ETH, XRP, DOT, LINK, SOL  
    - ✅ Connect with Coinbase, Binance, or Kraken  
    - ✅ Cancel Anytime
            """
        )

        if st.button("👉 Subscribe Monthly"):
            components.html(
                """
                <script>
                    window.open("https://buy.stripe.com/00w3cv3QgfpvegJ76H18c01", "_blank");
                </script>
                """,
                height=0,
                width=0
            )

    # === Pro Annual Plan ===
    with col3:
        st.markdown("### 🎯 Annual Pro Plan")
        st.markdown(
            "<p><span style='text-decoration: line-through;'>$299.99</span> &nbsp; <strong>Now Only $149.99 / year</strong></p>",
            unsafe_allow_html=True
        )

        st.markdown(
            """
🔥 **Limited Time Offer! (Save 50%)**  

- ✅ 30 Day Free Trial  
- ✅ 50% Annual Savings  
- ✅ Includes all Pro Plan Features  
- ✅ Cancel Anytime
            """
        )

        # Add space so button aligns with monthly plan
        st.markdown("<br><br>", unsafe_allow_html=True)

        if st.button("👉 Subscribe Annually"):
            components.html(
                """
                <script>
                    window.open("https://buy.stripe.com/9B628rfyY6SZ4G9aiT18c00", "_blank");
                </script>
                """,
                height=0,
                width=0
            )
