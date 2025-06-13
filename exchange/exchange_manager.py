from exchange.kraken import KrakenAPI
from exchange.binance import BinanceAPI
from exchange.coinbase import CoinbaseAPI

def get_exchange(exchange_name="kraken", mode="paper", api_keys=None):
    if exchange_name.lower() == "kraken":
        return KrakenAPI(mode=mode, api_keys=api_keys)
    elif exchange_name.lower() == "binance":
        return BinanceAPI(mode=mode, api_keys=api_keys)
    elif exchange_name.lower() == "coinbase":
        return CoinbaseAPI(mode=mode, api_keys=api_keys)
    else:
        raise ValueError(f"Unsupported exchange: {exchange_name}")
