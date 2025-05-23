# utils/kraken_auth.py

import krakenex
from utils.load_keys import API_KEY, API_SECRET

def get_kraken_clients():

    api = krakenex.API()
    api.key = API_KEY
    api.secret = API_SECRET

    return api, KrakenWrapper(api)

class KrakenWrapper:
    def __init__(self, api):
        self.api = api

    def get_account_balance(self):
        try:
            return self.api.query_private('Balance')
        except Exception as e:
            print(f"❌ Balance fetch error: {e}")
            return None