import requests
import time

class CoinbaseAPI:
    def __init__(self, mode="paper", api_keys=None):
        self.mode = mode
        self.api_keys = api_keys

    def get_balance(self):
        # Placeholder: You can expand this with real Coinbase account API access
        return {}

    def place_order(self, side, symbol, amount, order_type="market", price=None):
        # Simulate an order placement (expand with real auth later)
        print(f"[Coinbase] Simulating {order_type.upper()} order: {side.upper()} {amount} {symbol} at {price or 'market price'}")
        return {
            "order_id": f"simulated-{int(time.time())}",
            "status": "filled",
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "price": price or self.get_price(symbol)
        }

    def get_price(self, symbol):
        # Pull current market price using Coinbase public API
        try:
            url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot"
            response = requests.get(url)
            data = response.json()
            return float(data["data"]["amount"])
        except Exception as e:
            print(f"[Coinbase] Error fetching price for {symbol}: {e}")
            return 0.0


# === Public Utility Functions (for compatibility) ===

def get_prices():
    prices = {}
    supported = ["BTC", "ETH", "XRP", "DOT", "LINK", "SOL"]
    for coin in supported:
        try:
            url = f"https://api.coinbase.com/v2/prices/{coin}-USD/spot"
            response = requests.get(url)
            data = response.json()
            prices[coin] = float(data["data"]["amount"])
        except Exception as e:
            print(f"[Coinbase] Error fetching price for {coin}: {e}")
            prices[coin] = 0.0
    return prices


def get_balances(api_keys):
    # Placeholder – real implementation will need Coinbase OAuth or API key logic
    print("[Coinbase] Simulated get_balances()")
    return {
        "USD": 100000,
        "BTC": 0.5,
        "ETH": 2.0
    }


def place_order(side, symbol, amount, price=None):
    print(f"[Coinbase] Simulated {side.upper()} order for {amount} {symbol} at {price or 'market'}")
    return {
        "order_id": f"simulated-{int(time.time())}",
        "status": "filled"
    }


def cancel_order(order_id):
    print(f"[Coinbase] Simulated cancel of order {order_id}")
    return True
