import requests
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# === Price Fetch ===
def get_price_data():
    url = "https://api.kraken.com/0/public/Ticker"
    pairs = ["XXBTZUSD", "XETHZUSD", "SOLUSD", "XRPUSD", "DOTUSD", "LINKUSD"]
    try:
        response = requests.get(url, params={"pair": ",".join(pairs)})
        data = response.json().get("result", {})
        return {
            "BTC": float(data.get("XXBTZUSD", {}).get("c", [0])[0]),
            "ETH": float(data.get("XETHZUSD", {}).get("c", [0])[0]),
            "SOL": float(data.get("SOLUSD", {}).get("c", [0])[0]),
            "XRP": float(data.get("XRPUSD", {}).get("c", [0])[0]),
            "DOT": float(data.get("DOTUSD", {}).get("c", [0])[0]),
            "LINK": float(data.get("LINKUSD", {}).get("c", [0])[0]),
        }
    except Exception as e:
        print(f"❌ Failed to fetch price data: {e}")
        return {}

# === OHLCV Fetch ===
def fetch_kraken_ohlcv(pair="XXBTZUSD", interval=5):
    url = "https://api.kraken.com/0/public/OHLC"
    try:
        res = requests.get(url, params={"pair": pair, "interval": interval})
        data = res.json().get("result", {}).get(pair, [])
        df = pd.DataFrame(data, columns=[
            "time", "open", "high", "low", "close", "vwap", "volume", "count"
        ])
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df["close"] = df["close"].astype(float)
        return df
    except Exception as e:
        print(f"❌ Failed to fetch OHLCV: {e}")
        return pd.DataFrame()

# === RSI Calculation ===
def get_rsi(coin="BTC", interval=5):
    pair = {
        "BTC": "XXBTZUSD",
        "ETH": "XETHZUSD",
        "SOL": "SOLUSD",
        "XRP": "XRPUSD",
        "DOT": "DOTUSD",
        "LINK": "LINKUSD"
    }.get(coin.upper(), "XXBTZUSD")

    df = fetch_kraken_ohlcv(pair=pair, interval=interval)
    if df.empty or len(df) < 15:
        return None
    rsi = ta.rsi(df["close"], length=14)
    return round(rsi.dropna().iloc[-1], 2) if not rsi.empty else None

# === Bollinger Bandwidth Calculation ===
def get_bollinger_bandwidth(coin="BTC", interval=5):
    pair = {
        "BTC": "XXBTZUSD",
        "ETH": "XETHZUSD",
        "SOL": "SOLUSD",
        "XRP": "XRPUSD",
        "DOT": "DOTUSD",
        "LINK": "LINKUSD"
    }.get(coin.upper(), "XXBTZUSD")

    df = fetch_kraken_ohlcv(pair=pair, interval=interval)
    if df.empty or len(df) < 20:
        return None
    bb = ta.bbands(df["close"])
    if bb is not None and "BBU_20_2.0" in bb and "BBL_20_2.0" in bb:
        width = bb["BBU_20_2.0"].iloc[-1] - bb["BBL_20_2.0"].iloc[-1]
        return round(width / df["close"].iloc[-1], 4)
    return None
