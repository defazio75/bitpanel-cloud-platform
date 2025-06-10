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
from utils.load_keys import load_user_api_keys
from utils.kraken_auth import rate_limited_query_private

API_URL = "https://api.kraken.com"

# === Kraken Auth Helpers ===
def rate_limited_query_public(endpoint, params=None):
    url = f"{API_URL}/0/public/{endpoint}"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def rate_limited_query_private(endpoint, data=None, user_id=None, token=None):
    if data is None:
        data = {}
    if not user_id:
        raise ValueError("❌ user_id is required for private Kraken calls.")

    keys = load_user_api_keys(user_id, "kraken", token=token)
    api_key = keys["key"]
    api_secret = keys["secret"]

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
def get_live_balances(user_id, token=None):
    result = rate_limited_query_private("/0/private/Balance", {}, user_id, token=token)

    raw_balances = result.get("result", {})
    
    # Map Kraken's internal codes to readable symbols
    kraken_symbol_map = {
        "XXBT": "BTC",
        "XETH": "ETH",
        "ZUSD": "USD",
        "XXRP": "XRP",
        "DOT": "DOT",
        "LINK": "LINK",
        "SOL": "SOL"   
    }

    balances = {}
    for k_code, amount in raw_balances.items():
        symbol = kraken_symbol_map.get(k_code, k_code)  # fallback to raw code if not mapped
        balances[symbol] = float(amount)

    return balances

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
