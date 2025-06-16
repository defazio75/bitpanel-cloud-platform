from stripe import app  

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        price_id = data.get("price_id")

        session = stripe.checkout.Session.create(
            success_url="https://yourdomain.com/success",
            cancel_url="https://yourdomain.com/cancel",
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            subscription_data={
                "trial_period_days": 30,
                "metadata": {
                    "user_id": user_id
                }
            },
            metadata={
                "user_id": user_id
            }
        )
        return jsonify({'url': session.url})

    except Exception as e:
        return jsonify(error=str(e)), 400

if __name__ == "__main__":
    app.run(debug=True)
