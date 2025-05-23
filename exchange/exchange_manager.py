from exchanges.kraken import KrakenAPI
# (future: from exchanges.binance import BinanceAPI)
# (future: from exchanges.coinbase import CoinbaseAPI)

def get_exchange(exchange_name="kraken"):
    """
    Returns the correct exchange object.
    """
    if exchange_name.lower() == "kraken":
        return KrakenAPI()
    # elif exchange_name.lower() == "binance":
    #     return BinanceAPI()
    # elif exchange_name.lower() == "coinbase":
    #     return CoinbaseAPI()
    else:
        raise ValueError(f"Unsupported exchange: {exchange_name}")