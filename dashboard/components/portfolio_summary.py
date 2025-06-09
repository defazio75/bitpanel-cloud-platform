import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

from utils.config import get_mode
from utils.kraken_wrapper import get_live_balances, get_prices
from utils.firebase_db import load_portfolio_snapshot, load_performance_snapshot, load_coin_state, save_live_snapshot_from_kraken

st_autorefresh(interval=10_000, key="auto_refresh_summary")

def render_portfolio_summary(mode, user_id, token):
    st.title("📊 Portfolio Summary")

    # === Sync live balances before loading (LIVE MODE ONLY) ===
    if mode == "live":
        save_live_snapshot_from_kraken(user_id, token, mode)

    # === Load Portfolio ===
    snapshot = load_portfolio_snapshot(user_id, token, mode)

    if not snapshot:
        st.warning(f"No portfolio data found for {mode.upper()} mode.")
        return

    coins = list(snapshot.get("coins", {}).keys())
    prices = get_prices(user_id=user_id)
    
    # === Portfolio Header ===
    st.subheader("💰 Total Portfolio Value")
    col1, col2, col3 = st.columns(3)
    
    usd_balance = snapshot.get("usd_balance", 0.0)
    total_value = snapshot.get("total_value", usd_balance)

    col1.metric("Total Portfolio Value", f"${total_value:,.2f}")
    col2.metric("USD Balance", f"${usd_balance:,.2f}")
    col3.metric("BTC Price", f"${prices.get('BTC', 0):,.2f}")

    # === Portfolio Allocation Section ===
    st.subheader("📈 Portfolio Allocation")

    allocation_data = []
    table_data = []

    for coin, data in snapshot.get("coins", {}).items():
        amount = data.get("balance", 0.0)
        price = prices.get(coin, 0.0)
        usd_value_raw = amount * price
        usd_value = round(usd_value_raw, 2)

        # Get 24H change %
        price_info = prices.get(coin, {})
        if isinstance(price_info, dict):
            change_pct = price_info.get("change_pct", 0.0)
        else:
            change_pct = 0.0

        if usd_value > 0:
            allocation_data.append({
                "coin": coin,
                "value": float(usd_value)
            })
            table_data.append({
                "Coin": coin,
                "Amount": round(amount, 6),
                "USD Value": f"${usd_value:,.2f}",
                "24H Change": f"{change_pct:+.2f}%"
            })

    # Display in two columns: table + pie
    col1, col2 = st.columns([1.5, 1])
    with col1:
        if table_data:
            st.markdown("### 💡 Coin Holdings")
            st.dataframe(pd.DataFrame(table_data), use_container_width=True)
        else:
            st.warning("No coin holdings found.")

    with col2:
        if allocation_data:
            df = pd.DataFrame(allocation_data)
            fig = px.pie(df, names="coin", values="value", title="Asset Allocation")

            fig.update_traces(
                textinfo='label+percent',
                textposition='inside',
                hovertemplate='%{label}: $%{value:,.2f}<br>(%{percent})'
            )

            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(t=50, b=50, l=0, r=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No allocation data to plot.")

    # === Portfolio Performance ===
    st.subheader("📊 Portfolio Performance")
    performance_data = load_performance_snapshot(user_id, token, mode)
    if not performance_data:
        st.info("Performance data not available.")
    else:
        cols = st.columns(5)
        for i, (period, data) in enumerate(performance_data.items()):
            cols[i].metric(
                label=period,
                value=f"${data.get('profit', 0):,.2f}",
                delta=f"{data.get('pct', 0):.2f}%"
            )

    # === Strategy Breakdown ===
    st.subheader("🧠 Current Strategies")
    strategies = ["HODL", "RSI_5MIN", "RSI_1HR", "BOLL"]
    for coin in coins:
        state = load_coin_state(user_id, coin, token, mode)
        if not state:
            continue

        with st.expander(f"{coin} Strategy Breakdown"):
            for strategy in strategies:
                strat_data = state.get(strategy)
                if not strat_data:
                    continue
                amount = strat_data.get("amount", 0)
                usd_held = strat_data.get("usd_held", 0)
                status = strat_data.get("status", "Unknown")
                profit = strat_data.get("profit", 0)
                total_usd = round(amount * prices.get(coin, 0), 2) + usd_held
                st.write(
                    f"**{strategy}** | Status: `{status}` | Value: `${total_usd:,.2f}` | Profit: `${profit:,.2f}`"
                )

