import time
import hmac
import hashlib
import requests


class BinanceAPI:
    BASE_URL = "https://api.binance.com"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret.encode()

    def _get_headers(self):
        return {
            "X-MBX-APIKEY": self.api_key
        }

    def _sign_params(self, params):
        query_string = "&".join([f"{key}={val}" for key, val in params.items()])
        signature = hmac.new(self.api_secret, query_string.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def get_balance(self):
        """Fetch account balances (authenticated)"""
        endpoint = "/api/v3/account"
        url = self.BASE_URL + endpoint

        timestamp = int(time.time() * 1000)
        params = {"timestamp": timestamp}

        signed_params = self._sign_params(params)
        response = requests.get(url, headers=self._get_headers(), params=signed_params)

        if response.status_code != 200:
            print(f"❌ Binance Balance Error: {response.status_code} - {response.text}")
            return {}

        balances = response.json().get("balances", [])
        return {b["asset"]: float(b["free"]) for b in balances if float(b["free"]) > 0}

    def place_order(self, symbol, side, quantity, order_type="MARKET"):
        """Place a basic order (market only)"""
        endpoint = "/api/v3/order"
        url = self.BASE_URL + endpoint

        timestamp = int(time.time() * 1000)
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),  # BUY or SELL
            "type": order_type,
            "quantity": quantity,
            "timestamp": timestamp
        }

        signed_params = self._sign_params(params)
        response = requests.post(url, headers=self._get_headers(), params=signed_params)

        if response.status_code != 200:
            print(f"❌ Binance Order Error: {response.status_code} - {response.text}")
            return {}

        return response.json()

    def cancel_order(self, symbol, order_id):
        """Cancel an order (not used yet, but stubbed)"""
        endpoint = "/api/v3/order"
        url = self.BASE_URL + endpoint

        timestamp = int(time.time() * 1000)
        params = {
            "symbol": symbol.upper(),
            "orderId": order_id,
            "timestamp": timestamp
        }

        signed_params = self._sign_params(params)
        response = requests.delete(url, headers=self._get_headers(), params=signed_params)

        if response.status_code != 200:
            print(f"❌ Binance Cancel Error: {response.status_code} - {response.text}")
            return {}

        return response.json()
