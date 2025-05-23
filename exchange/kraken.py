import requests
import time
import urllib.parse
import hashlib
import hmac
import base64
import os
import json

class KrakenAPI:
    def __init__(self):
        keys_path = os.path.join('config', 'kraken.keys')
        with open(keys_path, 'r') as f:
            keys = json.load(f)
        self.api_key = keys['api_key']
        self.api_secret = keys['api_secret']
        self.api_url = "https://api.kraken.com"

    def _sign(self, urlpath, data, nonce):
        postdata = urllib.parse.urlencode(data)
        encoded = (str(nonce) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()

        mac = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        sigdigest = base64.b64encode(mac.digest())
        return sigdigest.decode()

    def _private_request(self, method, data=None):
        if data is None:
            data = {}
        urlpath = f"/0/private/{method}"
        url = self.api_url + urlpath

        nonce = str(int(1000*time.time()))
        data['nonce'] = nonce

        headers = {
            'API-Key': self.api_key,
            'API-Sign': self._sign(urlpath, data, nonce)
        }

        response = requests.post(url, headers=headers, data=data)
        return response.json()

    def _public_request(self, method, params=None):
        url = f"{self.api_url}/0/public/{method}"
        response = requests.get(url, params=params)
        return response.json()

    # === Public API Calls ===

    def get_ticker(self, pair="XXBTZUSD"):
        result = self._public_request("Ticker", {"pair": pair})
        return result.get('result', {})

    # === Private API Calls ===

    def get_account_balance(self):
        result = self._private_request("Balance")
        return result.get('result', {})

    def get_trade_balance(self, asset="ZUSD"):
        result = self._private_request("TradeBalance", {"asset": asset})
        return result.get('result', {})

    # (Future: Add place_order() etc.)
