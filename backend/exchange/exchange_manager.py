from exchange.kraken import KrakenAPI
from exchange.binance import BinanceAPI
from exchange.coinbase import CoinbaseAPI

def get_exchange(exchange_name, api_keys):
    if exchange_name.lower() == "kraken":
        return KrakenAPI(key=api_keys["key"], secret=api_keys["secret"])
    elif exchange_name.lower() == "binance":
        return BinanceAPI(key=api_keys["key"], secret=api_keys["secret"])
    elif exchange_name.lower() == "coinbase":
        return CoinbaseAPI(key=api_keys["key"], secret=api_keys["secret"])
    else:
        raise ValueError(f"Unsupported exchange: {exchange_name}")
