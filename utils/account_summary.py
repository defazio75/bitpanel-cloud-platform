import os
import json

def get_total_portfolio_value(mode="live"):
    if mode == "paper":
        try:
            path = os.path.join("data", "paper", "portfolio_snapshot.json")
            with open(path, "r") as f:
                data = json.load(f)
            return {
                'usd': data.get("usd_balance", 0.0),
                'btc': data["coins"].get("BTC", {}).get("balance", 0.0),
                'btc_price': data["coins"].get("BTC", {}).get("price", 0.0),
                'btc_usd_value': data["coins"].get("BTC", {}).get("value", 0.0),
                'total': data.get("total_value", 0.0)
            }
        except Exception as e:
            raise RuntimeError(f"Error reading paper portfolio snapshot: {e}")
    
    # LIVE MODE (Kraken)
    try:
        from utils.kraken_auth import get_kraken_clients
        from utils.kraken_wrapper import get_btc_price as get_current_price, get_kraken_balance

        balance_response = get_kraken_balance()

        if 'result' not in balance_response:
            print("⚠️ Kraken API returned unexpected response:")
            print(json.dumps(balance_response, indent=2))
            raise RuntimeError("Missing 'result' in Kraken balance response.")

        balances = balance_response['result']
        usd_value = float(balances.get('ZUSD', 0))
        btc_value = float(balances.get('XXBT', 0))
        btc_price = get_current_price()

        return {
            'usd': usd_value,
            'btc': btc_value,
            'btc_price': btc_price,
            'btc_usd_value': btc_value * btc_price,
            'total': usd_value + (btc_value * btc_price)
        }

    except Exception as e:
        raise RuntimeError(f"Unable to fetch Kraken portfolio value: {e}")