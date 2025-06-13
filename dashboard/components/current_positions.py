import streamlit as st
from utils.kraken_wrapper import get_prices
from utils.firebase_db import load_portfolio_snapshot
import pandas as pd
import os
from datetime import datetime

def calculate_live_portfolio_value(snapshot, prices):
    total = snapshot.get("usd_balance", 0.0)
    for coin, data in snapshot.get("coins", {}).items():
        balance = data.get("balance", 0.0)
        price = prices.get(coin, 0.0)
        total += round(balance * price, 2)
    return round(total, 2)

def render_current_positions(mode, user_id, token):
    st.title("Live Overview")
    st.caption("A real-time snapshot of your portfolio and active strategy activity.")

    # === Load Prices and Portfolio ===
    prices = get_prices(user_id=user_id)
    snapshot = load_portfolio_snapshot(user_id, token, mode)
    total_value = calculate_live_portfolio_value(snapshot, prices)
    usd_balance = snapshot.get("usd_balance", 0.0)
    coin_data = snapshot.get("coins", {})

    # === Count Active Strategies ===
    from utils.firebase_db import load_coin_state
    strategy_count = 0
    for coin in coin_data:
        state = load_coin_state(user_id=user_id, coin=coin, token=token, mode=mode)
        for strat in state:
            if state[strat].get("status") == "Active":
                strategy_count += 1

    # === Load Recent Trade Log ===
    trade_log_path = f"data/logs/trade_log_{mode}.csv"
    last_trade = "—"
    if os.path.exists(trade_log_path):
        df = pd.read_csv(trade_log_path)
        if not df.empty:
            last_row = df.sort_values("timestamp", ascending=False).iloc[0]
            ts = pd.to_datetime(last_row["timestamp"]).strftime("%I:%M %p")
            last_trade = f'{last_row["coin"]} - {last_row["strategy"]} - {last_row["action"].upper()} @ {last_row["price"]:.2f} ({ts})'

    # === Layout ===
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💼 Total Portfolio", f"${total_value:,.2f}")
    col2.metric("💰 USD Balance", f"${usd_balance:,.2f}")
    col3.metric("🤖 Bots Active", f"{strategy_count} strategies")
    col4.metric("⏱️ Last Trigger", last_trade)

    # === Per-Coin Strategy Cards ===
    st.markdown("---")
    st.subheader("📦 Current Position Details")

    supported_coins = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]
    strategy_list = ["HODL", "5min RSI", "1hr RSI", "Bollinger", "DCA Matrix"]

    for coin in supported_coins:
        coin_upper = coin.upper()
        coin_price = prices.get(coin_upper, 0.0)
        coin_balance = coin_data.get(coin_upper, {}).get("balance", 0.0)
        coin_usd_value = round(coin_balance * coin_price, 2)
        coin_state = load_coin_state(user_id=user_id, coin=coin_upper, token=token, mode=mode)

        table_rows = []
        active_count = 0

        for strat in strategy_list:
            s = coin_state.get(strat, {})
            status = s.get("status", "Inactive")
    
            if status != "Active":
                continue  # Skip strategies that are not active

            amount = s.get("amount", 0.0)
            usd_held = s.get("usd_held", 0.0)
            buy_price = s.get("buy_price", 0.0)

            in_market = amount > 0
            position_value = round(amount * coin_price, 2)
            assigned_usd = usd_held + position_value
            assigned_amt = round(assigned_usd / coin_price, 6) if coin_price else 0.0
            position_status = "In Market" if in_market else "In Cash"

            # Calculate P/L
            if amount > 0 and buy_price > 0:
                pl_value = round((coin_price - buy_price) * amount, 2)
                if pl_value > 0:
                    color = "#2ecc71"  # green
                    pl_display = f"<span style='color:{color}'>+${pl_value:,.2f}</span>"
                elif pl_value < 0:
                    color = "#e74c3c"  # red
                    pl_display = f"<span style='color:{color}'>-${abs(pl_value):,.2f}</span>"
                else:
                    pl_display = "—"
            else:
                pl_display = "—"

            if status == "Active":
                active_count += 1

            table_rows.append({
                "Strategy": strat,
                "Status": position_status,
                "Assigned Amt": f"{amount:.6f}",
                "USD Held": f"${usd_held:,.2f}",
                "Position Value": f"${position_value:,.2f}",
                "Buy Price": f"${buy_price:,.2f}" if buy_price else "—",
                "P/L": pl_display
            })

        df = pd.DataFrame(table_rows)
        df.index = [""] * len(df)  # Hide index
        with st.expander(f"\U0001F4B0 {coin_upper} — ${coin_usd_value:,.2f} | {coin_balance:.6f} {coin_upper} | {active_count} Bots Active", expanded=False):
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # === Final Trade Log Section ===
    st.markdown("---")
    st.subheader("📈 Recent Trades")

    if os.path.exists(trade_log_path):
        df = pd.read_csv(trade_log_path)
        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp", ascending=False).head(10)
            df["timestamp"] = df["timestamp"].dt.strftime("%b %d, %Y %I:%M %p")
            df_display = df[["timestamp", "coin", "strategy", "action", "price", "size"]]
            df_display.columns = ["Time", "Coin", "Strategy", "Action", "Price", "Size"]
            st.table(df_display)
        else:
            st.info("No trades found.")
    else:
        st.info("No trade log available.")
