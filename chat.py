import random
import json
import sqlite3
import torch
import re
from flask import jsonify

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

STATE_INITIAL = "initial"
STATE_BILLING_ADDRESS = "billing_address"
STATE_DELIVERY_ADDRESS_CONFIRMATION = "delivery_address_confirmation"
STATE_DELIVERY_ADDRESS = "delivery_address"
STATE_SELECT_PRODUCT = "select_product"

#creating the database
def create_database():
    conn = sqlite3.connect('user_data.db')  
    cursor = conn.cursor()
    
    

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL,
            orders TEXT NOT NULL,
            total_amount REAL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products(
            product_id INTEGER PRIMARY KEY,
            productname TEXT NOT NULL,
            model_name TEXT NOT NULL,
            price REAL DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS purchasers(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT NOT NULL,
            email TEXT NOT NULL,
            billing_address TEXT,
            delivery_address TEXT,
            purchase_status TEXT DEFAULT 'no'
        )
    ''')
    
    conn.commit()
    conn.close()

#create_database()

def insert_or_update_purchasers(name, contact, email, billing_address, delivery_address):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT ID FROM purchasers WHERE contact = ? OR email=?', (contact,email))
    existing_user = cursor.fetchone()

    if existing_user:
        user_id = existing_user[0]
        cursor.execute('''
            UPDATE purchasers
            SET name = ?, email=?, billing_address = ?, delivery_address = ?
            WHERE ID = ?
        ''', (name, email, billing_address, delivery_address, user_id))
    else:
        cursor.execute('''
            INSERT INTO purchasers (name, contact, email, billing_address, delivery_address, purchase_status)
            VALUES (?, ?, ?, ?, ?, 'no')
        ''', (name, contact, email, billing_address, delivery_address))

    conn.commit()
    conn.close()

def update_non_purchaser_status(name, contact, email):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE purchasers
        SET purchase_status = 'yes'
        WHERE name = ? AND contact = ? AND email = ?
    ''', (name, contact, email))
    
    conn.commit()
    conn.close()

'''def insert_pro(product_id,productname,model_name,price):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM products WHERE product_id = ?', (product_id,))
    existing_product = cursor.fetchone()
    if existing_product:
        print(f"Product with ID {product_id} already exists. Skipping insertion.")
    else:
        cursor.execute(
        INSERT INTO products(product_id, productname, model_name, price)
        VALUES (?, ?, ?,?)
    , (product_id, productname, model_name, price))

    conn.commit()
    conn.close()

def initialize_pro():
    products=[
        (101,"Barcode Scanner","BS-I201 S Bluetooth Barcode Scanner",8500.00),
        (102,"Barcode Scanner","BS-C103G Barcode Scanner",2000.00),
        (103,"Barcode Scanner","BS-i203G 2D Barcode Scanner",9000.00),
        (201,"Mouse","Champ Pixl Wired Gaming Mouse",1900.00),
        (202,"Mouse","Champ Ikon BM316 Bluetooth Wireless Mouse",1200.00),
        (203,"Mouse","Champ M120-Wired Optical Mouse",300.00),
        (301,"Keyboard","Champ Wired Keyboard",400.00),
        (302,"Keyboard","Champ Heavy Duty Keyboard",750.00),
        (303,"Keyboard","Champ Plus USB-A Wired Keybaord",500.00),
        (401,"Thermal Receipt Printer","RP 3160 GOLD",10000.00),
        (402,"Thermal Receipt Printer","RP 3230",6500.00),
        (403,"Thermal Receipt Printer","RP 3200 PLUS",8000.00),
        (501,"Touch POS System","TP 415C",50000.00),
        (502,"Touch POS System","TP 415C PRO",56000.00),
        (503,"Touch POS System","TP i415c K",60000.00)
    ]
    for product in products:
        insert_pro(product[0],product[1],product[2],product[3])

create_database()
initialize_pro()'''
#adding 'billing_address' and 'delivery_address' columns to users table
'''def add_columns_to_users_table():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN billing_address TEXT")
        cursor.execute("ALTER TABLE users ADD COLUMN delivery_addresss TEXT")
    except sqlite3.OperationalError as e:
        print(f"Error occurred: {e}")

    conn.commit()
    conn.close()

add_columns_to_users_table()'''
# creating order_details table
'''def create_order_details_table():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute(
        CREATE TABLE IF NOT EXISTS order_details (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    )

    conn.commit()
    conn.close()

create_order_details_table()'''


def insert_user_data(name, contact, email, billing_address, delivery_address, orders, total_amount):
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        orders_str = ', '.join([f"{order['quantity']} of {get_product_details_by_id(order['product'])[0][0]}" for order in orders])

        cursor.execute('''
            INSERT INTO users (name, contact, email, billing_address, delivery_address, orders, total_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, contact, email, billing_address, delivery_address, orders_str, total_amount))

        conn.commit()
        conn.close()

def get_available_products():
    conn=sqlite3.connect('user_data.db')
    cursor=conn.cursor()

    cursor.execute('SELECT product_id, productname,model_name, price FROM products')
    products=cursor.fetchall()

    conn.close()

    return [f"{product[1]} (ID : {product[0]}, Model : {product[2]}): ${product[3]:.2f}" for product in products]

def get_product_details(product_name):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT product_id, model_name, price FROM products WHERE productname=?', (product_name,))
    product_details = cursor.fetchall()


    conn.close()
    return product_details

def get_product_details_by_id(product_id):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT model_name, price FROM products WHERE product_id = ?', (product_id,))
    product_details = cursor.fetchall()
    
    conn.close()
    return product_details


def get_all_products():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT product_id,productname, model_name, price FROM products')
    all_products = cursor.fetchall()

    conn.close()

    return all_products

def get_product_by_name():
    product_name=input("Got it! Your email address is %1. Please enter the product name you want to purchase : \n 1. Barcode Scanner \n 2. Mouse \n 3. Keyboard \n 4. Thermal Receipt Printer \n 5. Touch POS System")

    product_details=get_product_details(product_name)

    if product_details:
        response=f"Product details for '{product_name}':\n"
        for product_id, model_name, price in product_details:
            response += f" - ID: {product_id}, Model : {model_name}, Price: ${price:.2f}\n"
        print(response)

        product_id=input("Please enter the product ID you want to order:")
        quantity=input("Please enter the quantity:")

        if not quantity.isdigit() or int(quantity) <= 0:
            print("Invalid quantity. Please enter a positive integer.")
            return
        
        print(f"You have selected {quantity} of product ID {product_id}.")
    else:
        print(f"Sorry, we couldn't find any product with the name '{product_name}'. Please try again.")

def add_total_amount():
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            ALTER TABLE users ADD COLUMN total_amount REAL DEFAULT 0
        ''')
        conn.commit()
        print("Column 'total_amount' added successfully.")
        
    except sqlite3.Error as e:
        print(f"An error occurred while adding the column: {e}")
        
    finally:
        if conn:
            conn.close()
add_total_amount()
#execute this to delete any data from the tables
'''def delete_user(user_id):
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        delete_statement='DELETE FROM sqlite_sequence WHERE seq=?'
        cursor.execute(delete_statement,(user_id,))
        conn.commit()
        print(f"User  with ID {user_id} has been deleted.")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        
    finally:
        if conn:
            conn.close()
delete_user()'''


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

user_name = None
user_contact = None
user_email = None
user_data= {
    "orders" : [],
    "current_state": STATE_INITIAL
}

def extract_name(msg):
    greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
    msg_lower = msg.lower().strip()
    if msg_lower in greetings:
        return None
    if len(msg.split()) == 1:
        return msg.strip()
    name_patterns = [
        r"my name is (\w+)",
        r"i am (\w+)",
        r"call me (\w+)",
        r"my name's (\w+)"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, msg, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def extract_contact(msg):
    phone_pattern = r'(\+?\d{1,3}[- ]?)?\d{10}'
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    
    phone_match = re.search(phone_pattern, msg)
    email_match = re.search(email_pattern, msg)
    
    return phone_match.group(0) if phone_match else None, email_match.group(0) if email_match else None

def extract_product_and_quantity(msg):
    pattern = r'(\d+)\s+([\w\s]+)' 
    matches = re.findall(pattern, msg, re.IGNORECASE)
    return [(match[1].strip(), match[0]) for match in matches]



def get_response(msg):
    global user_name ,user_contact ,user_email , user_data, model
    if user_name is None:
        name = extract_name(msg)
        if name:
            user_name = name
            return f"Nice to meet you, <strong>{user_name}!</strong>.<br> Please provide your contact number."

    contact, email = extract_contact(msg)
    if contact:
        user_contact = contact
        insert_or_update_purchasers(user_name,user_contact,"","","")
        return f"Got it! Your contact number is <strong>{user_contact}</strong>.<br> Provide your Emailid"
    if email:
        user_email = email
        insert_or_update_purchasers(user_name,user_contact,user_email,"","")
        user_data["current_state"]=STATE_BILLING_ADDRESS
        return f"Got it! Your email address is <strong>{user_email}</strong>.<br> Please provide your billing address."

    if user_data["current_state"]==STATE_BILLING_ADDRESS:
        user_data["billing_address"]=msg
        insert_or_update_purchasers(user_name,user_contact,user_email,user_data["billing_address"],"")
        user_data["current_state"]=STATE_DELIVERY_ADDRESS_CONFIRMATION
        return f"Thank you! Your billing address is <strong>{user_data['billing_address']}</strong>.<br> Is this the same as your delivery address? (Yes/No)"

    if user_data["current_state"]==STATE_DELIVERY_ADDRESS_CONFIRMATION:
        if msg.lower()=="yes":
            user_data["delivery_address"] = user_data["billing_address"]
            insert_or_update_purchasers(user_name,user_contact,user_email,user_data["billing_address"],user_data["delivery_address"])
            user_data["current_state"] = STATE_DELIVERY_ADDRESS
            user_data["current_state"] = STATE_SELECT_PRODUCT
            return f"Great! Your delivery address is the same as your billing address: <strong>{user_data['delivery_address']}</strong>.<br> Now, please select a product from the list below:<br> <ol> <li> Barcode Scanner </li> <li> Mouse </li> <li> Keyboard </li> <li> Thermal Receipt Printer </li> <li> Touch POS System </li> </ol>"
        elif msg.lower()=="no":
            user_data["current_state"] = STATE_DELIVERY_ADDRESS
            return "Please provide your delivery address."

    if user_data["current_state"] == STATE_DELIVERY_ADDRESS:
        user_data["delivery_address"] = msg
        insert_or_update_purchasers(user_name,user_contact,user_email,user_data["billing_address"],user_data["delivery_address"])
        response = f"Thank you! Your delivery address is <strong>{user_data['delivery_address']}</strong>.<br> Now, please select a product from the list below:<br> <ol> <li> Barcode Scanner </li> <li> Mouse </li> <li> Keyboard </li> <li> Thermal Receipt Printer </li> <li> Touch POS System </li> </ol>"
        user_data["current_state"] = STATE_SELECT_PRODUCT 
        return response

    if user_data["current_state"]==STATE_SELECT_PRODUCT:
        product_details = get_product_details(msg)
        if product_details:
            response = f" Availabe models for <strong> '{msg}':</strong><br>"
            response += "<table style='width:100%; border-collapse: collapse;'>"
            response += "<tr><th style='border: 1px solid black; padding: 8px;'>ID</th>"
            response += "<th style='border: 1px solid black; padding: 8px;'>Model</th>"
            response += "<th style='border: 1px solid black; padding: 8px;'>Price</th></tr>"
        
            for product_id, model_name, price in product_details:
                response += f"<tr><td style='border: 1px solid black; padding: 8px;'>{product_id}</td>"
                response += f"<td style='border: 1px solid black; padding: 8px;'>{model_name}</td>"
                response += f"<td style='border: 1px solid black; padding: 8px;'>Rs.{price:.2f}</td></tr>"
    
            response += "</table>"   
            response += "<br>Please enter the Product Id you want to order."
            user_data["current_product_details"] = product_details
            user_data["awaiting_product_id"] = True 
            return response


    if "current_product_details" in user_data and user_data.get("awaiting_product_id", False):
        if msg in [product[0] for product in user_data["current_product_details"]]:
            user_data["current_product_id"] = msg
            user_data["awaiting_product_id"] = False  
            user_data["awaiting_quantity"] = True
            return "Please enter the quantity you want to order."
        else:
            return "Invalid product ID. Please enter a valid product ID."


    if "current_product_id" in user_data and user_data.get("awaiting_quantity", False):
        if msg.isdigit():
            quantity = int(msg)
            if quantity > 0:
                user_data["orders"].append({"product": user_data["current_product_id"], "quantity": quantity})
                response = f"You have selected <strong>{quantity}</strong> of product ID <strong>{user_data['current_product_id']}</strong>."
                response += " Would you like to order anything else? (Yes/No/Remove)"
                user_data["awaiting_quantity"] = False 
                return response
            else:
                return "Invalid quantity. Please enter a positive integer."

    if msg.lower() == "yes":
        return "Please select the additional product name you'd like to order.<br>   <ol> <li>  Barcode Scanner </li> <li> Mouse </li><li>  Keyboard </li><li>  Thermal Receipt Printer </li> <li> Touch POS System</li> </ol>" 

    elif msg.lower() == "no":
        if user_data["orders"]:
            order_summary = "You have selected the following products:<br>\n"
            order_summary += "<table style='width:100%; border-collapse: collapse;'>"
            order_summary += "<tr><th style='border: 1px solid black; padding: 8px;'>ID</th>"
            order_summary += "<th style='border: 1px solid black; padding: 8px;'>Model</th>"
            order_summary += "<th style='border: 1px solid black; padding: 8px;'>Quantity</th>"
            order_summary += "<th style='border: 1px solid black; padding: 8px;'>Price</th>"
            order_summary += "<th style='border: 1px solid black; padding: 8px;'>Total</th></tr>"
            total_amount = 0.0
            for order in user_data["orders"]:
                product_id = order["product"]
                quantity = order["quantity"]
                product_info = get_product_details_by_id(product_id)

                if product_info:
                    model_name = product_info[0][0] 
                    price = product_info[0][1]
                    total_price = 0.0
                    total_price += price * quantity
                    order_summary += f"<tr><td style='border: 1px solid black; padding: 8px;'>{product_id}</td>"
                    order_summary += f"<td style='border: 1px solid black; padding: 8px;'>{model_name}</td>"
                    order_summary += f"<td style='border: 1px solid black; padding: 8px;'>{quantity}</td>"
                    order_summary += f"<td style='border: 1px solid black; padding: 8px;'>Rs.{price:.2f}</td>"
                    order_summary += f"<td style='border: 1px solid black; padding: 8px;'>Rs.{total_price:.2f}</td></tr>"
                    total_amount += total_price
                else:
                    order_summary += f"<tr><td colspan='4'>- {quantity} of Product ID {product_id} not found in the database.</td></tr>"
            order_summary += "</table>"
            order_summary += f"<br><strong>Total amount: Rs.{total_amount:.2f}</strong><br>"
            order_summary += f"<br> Type 'Yes' to add a product or Type 'Remove' to remove a product"
            order_summary += f"<br> Type 'Update' to change the quantity of any product"
            order_summary += "<br>Please type 'CONFIRM' to proceed to checkout."
            return order_summary
        else:
            return "You have not selected any products yet."

    if msg.lower()=="remove":
        if user_data["orders"]:
            response = "Please enter the Product ID of the item you want to remove from your order."
            user_data["awaiting_remove_id"] = True
            return response
        else:
            return "You have no products in your order to remove."
        
    
    if "awaiting_remove_id" in user_data and user_data["awaiting_remove_id"]:
        product_id_to_remove = msg
        product_found=False
        for order in user_data["orders"]:
            if order["product"] == product_id_to_remove:
                user_data["orders"].remove(order)
                product_found=True
                break
        user_data["awaiting_remove_id"] = False
        if product_found:
            return f"Product ID {product_id_to_remove} has been removed from your order. Would you like to order anything else or confirm your order? (yes/no/confirm)"
        else:
            return "Product ID not found in your order. Please enter a valid Product ID to remove."
        
    if msg.lower()=="update":
        if user_data["orders"]:
            response = "Please enter the Product ID of the item you want to update the quantity for."
            user_data["awaiting_update_id"] = True
            return response
        else:
            return "You have no products in your order to update."
        
    if "awaiting_update_id" in user_data and user_data["awaiting_update_id"]:
        product_id_to_update = msg
        product_found = False
        for order in user_data["orders"]:
            if order["product"] == product_id_to_update:
                product_found = True
                user_data["current_product_id"] = product_id_to_update
                user_data["awaiting_update_id"] = False
                user_data["awaiting_update_quantity"]=True
                return "Please enter the new quantity for this product."
        if not product_found:
            user_data["awaiting_update_id"] = False
            return "Product ID not found in your order. Please enter a valid Product ID to update."

    if "current_product_id" in user_data and user_data.get("awaiting_update_quantity", False):
        if msg.isdigit():
            new_quantity = int(msg)
            if new_quantity > 0:
                for order in user_data["orders"]:
                    if order["product"] == user_data["current_product_id"]:
                        order["quantity"] = new_quantity
                        break
                user_data["awaiting_update_quantity"] = False
                return f"The quantity for product ID {user_data['current_product_id']} has been updated to {new_quantity}. Would you like to confirm your order now? (yes/no)"
            else:
                return "Invalid quantity. Please enter a positive integer."
        else:
            return "I do not understand. Please enter a valid quantity."

    if msg.lower() == "confirm":
        total_amount=0.0
        for order in user_data["orders"]:
            product_id = order["product"]
            quantity = order["quantity"]

            product_info = get_product_details_by_id(product_id)

            if product_info:
                model_name=product_info[0][0]
                price = product_info[0][1] 
                total_amount += price * quantity
            else:
                return f"Error: Product ID {product_id} not found in the database. Cannot confirm order."
            
        insert_user_data(user_name, user_contact, user_email, user_data["billing_address"], user_data["delivery_address"], user_data["orders"],total_amount)
        update_non_purchaser_status(user_name,user_contact,user_email)
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email=?", (user_email,))
            user_id = cursor.fetchone()
            if user_id:
                user_id=user_id[0]

                for order in user_data["orders"]:
                    product_id=order["product"]
                    quantity=order["quantity"]
                    product_info=get_product_details_by_id(product_id)
                    if product_info:
                        price=product_info[0][1]
                        total_price=price*quantity
                        model_name=product_info[0][0]
                        cursor.execute('''
                                       INSERT INTO order_details(user_id,product_id,product_name,quantity,total_amount)
                                       VALUES (?,?,?,?,?)
                                       ''',(user_id,product_id,model_name,quantity,total_price))
                conn.commit()
                return (f"Your order has been confirmed! "
                        f"Please click the link to proceed to checkout: "
                        f"<a href='http://127.0.0.1:5000/checkout/{user_id}'>Checkout</a>.")
            else:
                return {"answer": "There was an error confirming your order. Please try again."}

    sentence = tokenize(msg)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                return random.choice(intent['responses'])
    
    return "I do not understand..."


if __name__ == "__main__":
    print("Let's chat! (type 'quit' to exit)")
    while True:
        sentence = input("You: ")
        if sentence == "quit":
            break

        resp = get_response(sentence)
        print(resp)