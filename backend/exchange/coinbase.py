import time
import hmac
import hashlib
import requests
import base64


class CoinbaseAPI:
    BASE_URL = "https://api.exchange.coinbase.com"

    def __init__(self, api_key, api_secret, passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.passphrase = passphrase

    def _get_headers(self, method, request_path, body=""):
        timestamp = str(time.time())
        message = f"{timestamp}{method}{request_path}{body}"
        hmac_key = base64.b64decode(self.api_secret)
        signature = hmac.new(hmac_key, message.encode("utf-8"), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode("utf-8")

        return {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature_b64,
            "CB-ACCESS-TIMESTAMP": timestamp,
            "CB-ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json"
        }

    def get_balance(self):
        """Fetch account balances"""
        method = "GET"
        path = "/accounts"
        url = self.BASE_URL + path

        headers = self._get_headers(method, path)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Coinbase Balance Error: {response.status_code} - {response.text}")
            return {}

        accounts = response.json()
        return {acc["currency"]: float(acc["available"]) for acc in accounts if float(acc["available"]) > 0}

    def place_order(self, product_id, side, size, order_type="market"):
        """Place a market order"""
        method = "POST"
        path = "/orders"
        url = self.BASE_URL + path

        body = {
            "type": order_type,
            "side": side,
            "product_id": product_id,
            "size": str(size)
        }

        import json
        body_json = json.dumps(body)
        headers = self._get_headers(method, path, body_json)

        response = requests.post(url, headers=headers, data=body_json)

        if response.status_code != 200:
            print(f"❌ Coinbase Order Error: {response.status_code} - {response.text}")
            return {}

        return response.json()

    def cancel_order(self, order_id):
        """Cancel an order"""
        method = "DELETE"
        path = f"/orders/{order_id}"
        url = self.BASE_URL + path

        headers = self._get_headers(method, path)
        response = requests.delete(url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Coinbase Cancel Error: {response.status_code} - {response.text}")
            return {}

        return response.json()
