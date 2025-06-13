import requests

def get_prices():
    try:
        response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=USD")
        data = response.json()
        return {
            "BTC": 1 / float(data["data"]["rates"]["BTC"]),
            "ETH": 1 / float(data["data"]["rates"]["ETH"]),
            "XRP": 1 / float(data["data"]["rates"]["XRP"]),
            "DOT": 1 / float(data["data"]["rates"]["DOT"]),
            "LINK": 1 / float(data["data"]["rates"]["LINK"]),
            "SOL": 1 / float(data["data"]["rates"]["SOL"]),
        }
    except Exception as e:
        print("❌ Coinbase get_prices error:", e)
        return {}

def get_balances(api_keys):
    # Coinbase Pro uses OAuth or API key/secret with HMAC
    # Placeholder for Coinbase balance logic
    print("⚠️ Coinbase API balance fetching not implemented yet.")
    return {}

def place_order(api_keys, symbol, side, amount, price=None):
    print(f"⚠️ [Coinbase] Simulated {side} order for {amount} {symbol} at {price or 'market'} price.")
    return {"status": "simulated", "id": "test123"}

def cancel_order(api_keys, order_id):
    print(f"⚠️ [Coinbase] Simulated cancel for order {order_id}.")
    return True
