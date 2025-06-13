from exchange.kraken import KrakenAPI
# (future: from exchanges.binance import BinanceAPI)
# (future: from exchanges.coinbase import CoinbaseAPI)

def get_exchange(exchange_name="kraken", mode="paper", api_keys=None):
    """
    Returns the correct exchange object.
    """
    if exchange_name.lower() == "kraken":
        return KrakenAPI(mode=mode, api_keys=api_keys)
    # elif exchange_name.lower() == "binance":
    #     return BinanceAPI()
    # elif exchange_name.lower() == "coinbase":
    #     return CoinbaseAPI()
    else:
        raise ValueError(f"Unsupported exchange: {exchange_name}")
