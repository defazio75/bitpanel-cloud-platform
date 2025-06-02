# utils/kraken_wrapper.py

import time
import requests
import base64
import hashlib
import hmac
from urllib.parse import urlencode
import json
import os
import pandas as pd
import streamlit as st
from utils.load_keys import load_api_keys

API_URL = "https://api.kraken.com"

# === Kraken Auth Helpers ===
def rate_limited_query_public(endpoint, params=None):
    url = f"{API_URL}/0/public/{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def rate_limited_query_private(endpoint, data=None, user_id=None):
    if data is None:
        data = {}

    if not user_id:
        raise ValueError("❌ user_id is required for private Kraken calls.")

    keys = load_api_keys(user_id=user_id)
    api_key = keys.get("key")
    api_secret = keys.get("secret")

    print("🔑 API KEY (first 6 chars):", api_key[:6], "…")
    print("🔑 API SECRET (first 6 chars):", api_secret[:6], "…")

    if not api_key or not api_secret:
        raise ValueError("❌ Missing Kraken API keys.")

    path = f"/0/private/{endpoint}"
    url = API_URL + path
    nonce = str(int(1000 * time.time()))
    data["nonce"] = nonce

    post_data = urlencode(data)
    encoded = (nonce + post_data).encode()
    message = path.encode() + hashlib.sha256(encoded).digest()

    try:
        signature = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)
        sig_digest = base64.b64encode(signature.digest())
    except Exception as e:
        raise ValueError(f"❌ Signature generation failed. Likely invalid API secret. Error: {e}")

    headers = {
        "API-Key": api_key,
        "API-Sign": sig_digest.decode()
    }

    response = requests.post(url, headers=headers, data=data)

    print("🐙 Kraken raw response:", response.text)

    try:
        response.raise_for_status()
        raw = response.json()

        if raw.get("error"):
            print("❌ Kraken returned errors:", raw["error"])

        return raw
    except Exception as e:
        print(f"❌ Exception from Kraken request: {e}")
        return {"error": [str(e)]}


# === Live Price Fetching ===
def get_prices(user_id=None):
    pairs = {
        "BTC": "XXBTZUSD",
        "ETH": "XETHZUSD",
        "SOL": "SOLUSD",
        "XRP": "XXRPZUSD",
        "DOT": "DOTUSD",
        "LINK": "LINKUSD"
    }

    prices = {}
    try:
        ticker = rate_limited_query_public("Ticker", {"pair": ",".join(pairs.values())})
        for coin, kraken_pair in pairs.items():
            prices[coin] = float(ticker["result"][kraken_pair]["c"][0])
    except Exception as e:
        print(f"❌ Error fetching live prices: {e}")
    return prices

# === Live Balances (Private API) ===
def get_live_balances(user_id=None):
    try:
        raw = rate_limited_query_private("Balance", user_id=user_id)
        balances = raw.get("result", {})
        print("🔍 RAW BALANCES:", json.dumps(balances, indent=2))
        mapped = {}

        for k, v in balances.items():
            amount = float(v)
            if amount < 1e-6:  # Ignore dust
                continue
            if k == "XXBT":
                mapped["BTC"] = amount
            elif k == "XETH":
                mapped["ETH"] = amount
            elif k == "SOL":
                mapped["SOL"] = amount
            elif k == "XXRP":
                mapped["XRP"] = amount
            elif k == "DOT":
                mapped["DOT"] = amount
            elif k == "LINK":
                mapped["LINK"] = amount
            elif k == "ZUSD":
                mapped["USD"] = amount

        print("✅ Cleaned balances:", mapped)
        return mapped
    except Exception as e:
        print(f"❌ Error fetching live balances: {e}")
        return {}

def get_prices_with_change():
    pairs = {
        "BTC": "XXBTZUSD",
        "ETH": "XETHZUSD",
        "SOL": "SOLUSD",
        "XRP": "XXRPZUSD",
        "DOT": "DOTUSD",
        "LINK": "LINKUSD"
    }

    results = {}
    try:
        ticker = rate_limited_query_public("Ticker", {"pair": ",".join(pairs.values())})
        for coin, kraken_pair in pairs.items():
            info = ticker["result"][kraken_pair]
            current = float(info["c"][0])
            open_price = float(info["o"])
            change = current - open_price
            pct_change = (change / open_price) * 100 if open_price else 0

            results[coin] = {
                "price": current,
                "change": round(change, 2),
                "pct_change": round(pct_change, 2)
            }
    except Exception as e:
        print(f"❌ Error fetching extended price data: {e}")
    return results

# === BTC-only convenience ===
def get_btc_price():
    try:
        result = rate_limited_query_public("Ticker", {"pair": "XXBTZUSD"})
        return float(result["result"]["XXBTZUSD"]["c"][0])
    except:
        return 0

@st.cache_data(ttl=60)
def get_rsi(coin, interval='1h', length=14):
    pair = f"{coin}USD"
    interval_map = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '1h': 60,
        '4h': 240,
        '1d': 1440
    }
    kraken_interval = interval_map.get(interval, 60)

    url = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={kraken_interval}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json().get('result', {})
    key = next((k for k in data if k != 'last'), None)
    if not key:
        return None

    ohlc = data[key]
    closes = pd.Series([float(entry[4]) for entry in ohlc])

    if len(closes) < length + 1:
        return None

    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=length, min_periods=length).mean()
    avg_loss = loss.rolling(window=length, min_periods=length).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return round(rsi.iloc[-1], 2) if not rsi.empty else None

@st.cache_data(ttl=60)
def get_bollinger_bandwidth(coin, interval='1h', length=20):
    pair = f"{coin}USD"
    interval_map = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '1h': 60,
        '4h': 240,
        '1d': 1440
    }
    kraken_interval = interval_map.get(interval, 60)

    url = f"https://api.kraken.com/0/public/OHLC?pair={pair}&interval={kraken_interval}"
    response = requests.get(url)
    if response.status_code != 200:
        return None

    data = response.json().get('result', {})
    key = next((k for k in data if k != 'last'), None)
    if not key:
        return None

    ohlc = data[key]
    closes = pd.Series([float(entry[4]) for entry in ohlc])

    if len(closes) < length:
        return None

    sma = closes.rolling(window=length).mean()
    std = closes.rolling(window=length).std()
    upper = sma + (std * 2)
    lower = sma - (std * 2)

    last_bb = (upper.iloc[-1] - lower.iloc[-1]) / sma.iloc[-1]
    return round(last_bb, 4)

def save_portfolio_snapshot(mode="live", auto_rebalance=False, user_id=None):
    if not user_id:
        raise ValueError("❌ user_id is required to save portfolio snapshot.")

    balances = get_live_balances(user_id=user_id)
    prices = get_prices(user_id=user_id)

    snapshot = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_value": 0,
        "usd_balance": balances.get("USD", 0),
        "coins": {}
    }

    total = snapshot["usd_balance"]
    live_portfolio = {"USD": snapshot["usd_balance"]}

    for coin in ["BTC", "ETH", "SOL", "XRP", "DOT", "LINK"]:
        amt = max(0, balances.get(coin, 0))
        price = prices.get(coin, 0)
        value = round(amt * price, 2) if amt and price else 0.0

        snapshot["coins"][coin] = {
            "balance": amt,
            "price": price,
            "value": value
        }

        live_portfolio[coin] = amt
        total += value

        print(f"✅ {mode.upper()} {coin} → amt={amt}, price={price}, value={value}")

    snapshot["total_value"] = round(total, 2)

    # 🔥 Save to Firebase only
    from utils.firebase_db import save_portfolio_snapshot_to_firebase
    token = st.session_state.user.get("token")
    if user_id and token:
        save_portfolio_snapshot_to_firebase(user_id, snapshot, token, mode)

    # Optional: live auto-rebalance
    if auto_rebalance and mode == "live":
        try:
            from bots.rebalance_bot import rebalance_hodl
            rebalance_hodl(user_id=user_id)
        except Exception as e:
            print(f"❌ Failed to auto-rebalance: {e}")
