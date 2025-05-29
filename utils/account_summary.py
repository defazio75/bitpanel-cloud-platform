import os
import json
from utils.kraken_wrapper import get_live_balances, get_btc_price

def get_total_portfolio_value(mode="live", user_id=None):
    if not user_id:
        raise ValueError("❌ user_id is required to fetch portfolio summary.")

    if mode == "paper":
        try:
            path = os.path.join("data", f"json_paper/{user_id}/portfolio/portfolio_snapshot.json")
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
        balances = get_live_balances(user_id=user_id)
        btc_price = get_btc_price()

        usd_value = balances.get('USD', 0.0)
        btc_value = balances.get('BTC', 0.0)

        return {
            'usd': usd_value,
            'btc': btc_value,
            'btc_price': btc_price,
            'btc_usd_value': btc_value * btc_price,
            'total': usd_value + (btc_value * btc_price)
        }

    except Exception as e:
        raise RuntimeError(f"Unable to fetch live portfolio value: {e}")
