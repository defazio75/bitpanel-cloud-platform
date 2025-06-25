from flask import request, jsonify
from utils.firebase_db import load_portfolio_snapshot
from utils.kraken_wrapper import get_prices
import controller

app = Flask(__name__)

@app.route('/prices', methods=['GET'])
def prices_endpoint():
    # if you need auth, grab user_id from headers or query args
    user_id = request.args.get('user_id')
    prices = get_prices(user_id)
    return jsonify(prices)

@app.route('/portfolio-snapshot', methods=['GET'])
def portfolio_snapshot():
    # read params
    user_id = request.args.get('user_id')
    mode    = request.args.get('mode')
    # assume client sends token in Authorization header: "Bearer <idToken>"
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.split(' ')[1] if ' ' in auth_header else None

    if not user_id or not mode or not token:
        return jsonify({"error":"Missing user_id, mode or token"}), 400

    # load from firebase or kraken_wrapper under the hood
    data = load_portfolio_snapshot(user_id=user_id, token=token, mode=mode)
    return jsonify(data)

@app.route('/manual_trade', methods=['POST'])
def manual_trade():
    trade_data = request.json
    result = controller.execute_manual_trade(trade_data)
    return jsonify(result)

@app.route('/reset_paper', methods=['POST'])
def reset_paper():
    controller.reset_paper_account()
    return jsonify({"status": "success"})

@app.route('/strategies', methods=['GET'])
def get_strategies():
    data = controller.get_strategy_allocations()
    return jsonify(data)

@app.route('/positions', methods=['GET'])
def get_positions():
    data = controller.get_active_positions()
    return jsonify(data)

@app.route('/performance', methods=['GET'])
def get_performance():
    data = controller.get_performance_metrics()
    return jsonify(data)

@app.route('/user_profile', methods=['GET'])
def user_profile():
    user_id = request.args.get('user_id')
    # if you need to validate a token, do so here (e.g. controller.verify_token)
    profile = controller.get_user_profile(user_id)  # should return e.g. { name, role, ... }
    return jsonify(profile or {}), 200

@app.route('/api_keys', methods=['GET'])
def get_api_keys():
    user_id = request.args.get('user_id')
    # your controller.load_user_api_keys already handles token+exchange inside
    data = controller.load_user_api_keys(user_id)
    return jsonify(data or {})

@app.route('/api_keys', methods=['POST'])
def save_api_keys():
    body = request.json
    user_id = body["user_id"]
    exchange = body["exchange"]
    key = body["key"]
    secret = body["secret"]
    controller.save_user_api_keys(user_id, exchange, key, secret)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)