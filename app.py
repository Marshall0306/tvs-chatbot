from flask import Flask, render_template, request, jsonify,redirect,url_for
import sqlite3

from chat import get_response



app = Flask(__name__)

@app.route('/')
def home():
    return render_template('base.html')


@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    if isinstance(response, dict) and "redirect" in response:
        return jsonify(response)  
    else:
        message = {"answer": response}
        return jsonify(message)

@app.route('/checkout/<int:user_id>')
def checkout(user_id):
    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            user_info = {
                "name": user[1],
                "contact": user[2],
                "email": user[3],
                "orders": user[4],
                "total_amount": user[5]
            }
            orders = parse_orders(user_info['orders'])
            user_info['orders'] = orders 
            return render_template('checkout.html', user=user_info)
        else:
            return "User  not found", 404

def parse_orders(orders_str):
    orders = []
    for order in orders_str.split(', '):
        quantity, product_name = order.split(' of ')
        orders.append({"quantity": int(quantity), "product_name": product_name})
    return orders
@app.route('/payment_successful')
def payment_successful():
    return render_template('payment_successful.html')

@app.route('/process_payment', methods=['POST'])
def process_payment(): 
    
    return redirect(url_for('payment_successful'))

    
if __name__ == "__main__":
    app.run(debug=True)