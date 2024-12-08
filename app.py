import decimal
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for
from pymongo import MongoClient
from flask import session 
from decimal import Decimal

from bson import ObjectId
from datetime import datetime, timedelta
app = Flask(__name__)
# client = MongoClient('mongodb://localhost:27017/')
client = MongoClient(os.getenv("MONGO_URI"))
db = client.quickcartDb
collection = db['products']
users_collection = db['customer']
cart_collection =db['order']
admin_collection =db['admin']
deliveries_collection =db['deliveries']
cancellation_collection =db['cancellation']
app.secret_key = 'whekjrherlwjerlwjerlkwejrkwensmend'
@app.route('/home')
def main():
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/promotions')
def promotions():
    return render_template('promotions.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/products/<category>')
def get_products(category):
    products = list(collection.find({"category": category}))
    for product in products:
        product['_id'] = str(product['_id'])
    return render_template('products.html', products=products)
@app.route('/cancellation_details')
def cancellation_details():
    cancellations = cancellation_collection.find()
    return render_template('cancellation_details.html', cancellations=cancellations)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Check if the user is an admin
    admin = admin_collection.find_one({'username': username, 'password': password})
    if admin:
        # Store the admin username in the session
        session['username'] = username
        # Redirect admin to all_products.html
        return redirect('/all_products')
    
    # If the user is not an admin, check if it's a regular user
    user = users_collection.find_one({'username': username, 'password': password})
    if user:
        # Store the regular user username in the session
        session['username'] = username
        return jsonify({'success': True, 'message': 'Login successful', 'username': username})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})
@app.route('/order')
def order():
    orders = cart_collection.find()
    return render_template('admin_orders.html', orders=orders)
@app.route('/all_products')
def all_products():
    # Fetch all products from the database
    products = collection.find()
    # Convert the cursor to a list of dictionaries
    products = list(products)
    # Render the all_products.html template with the products data
    return render_template('all_products.html', products=products)

@app.route('/cancelled_orders')
def cancelled_orders():
    if 'username' in session:
        username = session['username']
        cancelled_orders = cancellation_collection.find({'username': username})
        return render_template('cancelled_user.html', cancelled_orders=cancelled_orders)
    else:
        return "You are not logged in."

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'username' in session:
        username = session['username']
    else:
        # If not logged in, redirect to login page
        return redirect(url_for('login'))

    # Get the order details from the POST request
    order_details = request.json

    # Add the username to the order details
    order_details['username'] = username
  

    # Add expected delivery date if delivery option is selected
    if order_details['deliveryOption'] == 'delivery':
        expected_delivery = datetime.now() + timedelta(days=4)
        order_details['expectedDelivery'] = expected_delivery.strftime('%Y-%m-%d')

    # Insert the order details into the deliveries_collection
    result = deliveries_collection.insert_one(order_details)

    # Check if the insertion was successful
    if result.inserted_id:
        return jsonify({'message': 'Order placed successfully!'}), 200
    else:
        return jsonify({'message': 'Failed to place order!'}), 500
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    username = session.get('username')
    if username:
        cart_collection.delete_many({'username': username})
        return jsonify({'message': 'Cart data cleared successfully!'}), 200
    else:
        return jsonify({'message': 'Failed to clear cart data! User not logged in!'}), 401

@app.route('/add_product', methods=['POST'])
def add_product():
    # Convert ImmutableMultiDict to dictionary
    product_data = request.form.to_dict()
    
    # Insert the product into the database
    collection.insert_one(product_data)
    
    # Return a JSON response indicating success
    return jsonify({'message': 'Product added successfully'})


@app.route('/delete_product/<product_id>', methods=['GET'])
def delete_product(product_id):
    # Delete the product from the database based on the product ID
    result = collection.delete_one({'productid': product_id})
    if result.deleted_count == 1:
        return redirect(url_for('all_products'))
    else:
        return "Product not found", 404


@app.route('/get_product/<string:_id>', methods=['GET'])
def get_product(_id):
    try:
        # Retrieve the product from the database based on the product ID
        product = collection.find_one({'_id': ObjectId(_id)})
        if product:
            # Convert ObjectId to string before returning JSON
            product['_id'] = str(product['_id'])
            return jsonify(product), 200
        else:
            return 'Product not found', 404
    except Exception as e:
        return str(e), 500
 
@app.route('/edit_product/<product_id>', methods=['POST'])
def edit_product(product_id):
    # Get updated product data from the request
    updated_product_data = request.form.to_dict()
    print(updated_product_data)
    # Update the product in the database based on the product ID
    result = collection.update_one({'productid': product_id}, {'$set': updated_product_data})
    if result.modified_count == 1:
        return 'Product updated successfully', 200
    else:
        return 'Product not found', 404
#  @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     if 'username' in session:
#         username = session['username']
        
#         # Retrieve JSON data from request
#         data = request.json
#         productName = data.get('productName')
#         productSize = data.get('productSize')
#         quantity = data.get('quantity')
#         productPrice = data.get('productPrice')

#         # Check if all required keys are present
#         if productName is None or productSize is None or quantity is None or productPrice is None:
#             return jsonify({'success': False, 'message': 'Missing form data'})

#         # Check if the item already exists in the cart
#         existing_item = cart_collection.find_one({'username': username, 'productName': productName, 'productSize': productSize})
        
#         if existing_item:
#             # If the item exists, update the quantity
#             new_quantity = int(existing_item['quantity']) + int(quantity)
#             cart_collection.update_one({'_id': existing_item['_id']}, {'$set': {'quantity': new_quantity}})
#             return jsonify({'success': True, 'message': 'Item quantity updated in cart'})

#         # Save cart items with username
#         cart_item = {
#             'username': username,
#             'productName': productName,
#             'productSize': productSize,
#             'quantity': quantity,
#             'productPrice': productPrice
#         }
#         cart_collection.insert_one(cart_item)
#         return jsonify({'success': True, 'message': 'Item added to cart successfully'})
#     else:
#         return jsonify({'success': False, 'message': 'User not logged in'})

# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     if 'username' in session:
#         username = session['username']
        
#         # Retrieve JSON data from request
#         data = request.json
#         productName = data.get('productName')
#         productSize = data.get('productSize')
#         quantity = data.get('quantity')
#         productPrice = data.get('productPrice')

#         # Check if all required keys are present
#         if productName is None or productSize is None or quantity is None or productPrice is None:
#             return jsonify({'success': False, 'message': 'Missing form data'})

#         # Check if the item already exists in the cart
#         existing_item = cart_collection.find_one({'username': username, 'productName': productName, 'productSize': productSize})
        
#         if existing_item:
#             # If the item exists, update the quantity
#             new_quantity = int(existing_item['quantity']) + int(quantity)
#             cart_collection.update_one({'_id': existing_item['_id']}, {'$set': {'quantity': new_quantity}})
#             return jsonify({'success': True, 'message': 'Item quantity updated in cart'})

#         # Save cart items with username
#         cart_item = {
#             'username': username,
#             'productName': productName,
#             'productSize': productSize,
#             'quantity': quantity,
#             'productPrice': productPrice
#         }
#         cart_collection.insert_one(cart_item)
#         return jsonify({'success': True, 'message': 'Item added to cart successfully'})
#     else:
#         return jsonify({'success': False, 'message': 'User not logged in'})

# @app.route('/update_quantity', methods=['POST'])
# def update_quantity():
#     if 'username' in session:
#         username = session['username']
        
#         # Retrieve JSON data from request
#         data = request.json
#         _id = data.get('id')
#         quantity = data.get('quantity')

#         # Check if all required keys are present
#         if _id is None or quantity is None:
#             return jsonify({'success': False, 'message': 'Missing form data'})

#         # Update the quantity of the item in the cart
#         cart_collection.update_one({'_id': ObjectId(_id), 'username': username}, {'$set': {'quantity': quantity}})
#         return jsonify({'success': True, 'message': 'Item quantity updated in cart'})
#     else:
#         return jsonify({'success': False, 'message': 'User not logged in'})

# @app.route('/delete_product', methods=['POST'])
# def delete_product():
#     if 'username' in session:
#         username = session['username']
        
#         # Retrieve JSON data from request
#         data = request.json
#         _id = data.get('id')

#         # Check if all required keys are present
#         if _id is None:
#             return jsonify({'success': False, 'message': 'Missing form data'})

#         # Delete the item from the cart
#         cart_collection.delete_one({'_id': ObjectId(_id), 'username': username})
#         return jsonify({'success': True, 'message': 'Item deleted from cart'})
#     else:
#         return jsonify({'success': False, 'message': 'User not logged in'})



# @app.route('/add_to_cart', methods=['POST'])
# def add_to_cart():
#     if 'username' in session:
#         username = session['username']
        
#         # Retrieve JSON data from request
#         data = request.json
#         productName = data.get('productName')
#         productSize = data.get('productSize')
#         quantity = data.get('quantity')
#         productPrice = data.get('productPrice')

#         # Check if all required keys are present
#         if productName is None or productSize is None or quantity is None or productPrice is None:
#             return jsonify({'success': False, 'message': 'Missing form data'})
        
#         # Save cart items with username
#         cart_item = {
#             'username': username,
#             'productName': productName,
#             'productSize': productSize,
#             'quantity': quantity,
#             'productPrice': productPrice
#         }
#         cart_collection.insert_one(cart_item)
#         return jsonify({'success': True, 'message': 'Item added to cart successfully'})
#     else:
#         return jsonify({'success': False, 'message': 'User not logged in'})

# @app.route('/add_to_cart', methods=['POST'])
# # def add_to_cart():
# #     if 'username' in session:  # Check if user is logged in
# #         username = session['username']
# #         # Get cart items from form submission
# #         product_name = request.form['product_name']
# #         product_size = request.form['product_size']
# #         quantity = request.form['quantity']
# #         product_price = request.form['product_price']
        
# #         # Save cart items with user ID
# #         cart_item = {
# #             'username': username,
# #             'product_name': product_name,
# #             'product_size': product_size,
# #             'quantity': quantity,
# #             'product_price': product_price
# #         }
# #         cart_collection.insert_one(cart_item)  # Assuming cart_collection is your MongoDB collection for storing cart items
        
# #         return redirect(url_for('cart'))  # Redirect to cart page after adding item
# #     else:
# #         # User is not logged in, handle accordingly
# #         return redirect(url_for('login'))
@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    data = request.json
    cancellation_collection.insert_one(data)
    return jsonify({'message': 'Order cancelled successfully!'})
@app.route('/delete_delivery', methods=['POST'])
def delete_delivery():
    data = request.json
    username = data["username"]
    deliveries_collection.delete_many({"username": username})
    return jsonify({"success": True, "message": "Delivery records deleted successfully."})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'username' in session:
        username = session['username']
        
        # Retrieve JSON data from request
        data = request.json
        productName = data.get('productName')
        productSize = data.get('productSize')
        quantity = data.get('quantity')
        productPrice = data.get('productPrice')

        # Check if all required keys are present
        if productName is None or productSize is None or quantity is None or productPrice is None:
            return jsonify({'success': False, 'message': 'Missing form data'})

        # Check if the item already exists in the cart
        existing_item = cart_collection.find_one({'username': username, 'productName': productName, 'productSize': productSize})
        
        if existing_item:
            # If the item exists, update the quantity
            new_quantity = int(existing_item['quantity']) + int(quantity)
            cart_collection.update_one({'_id': existing_item['_id']}, {'$set': {'quantity': new_quantity}})
            return jsonify({'success': True, 'message': 'Item quantity updated in cart'})

        # Save cart items with username
        cart_item = {
            'username': username,
            'productName': productName,
            'productSize': productSize,
            'quantity': quantity,
            'productPrice': productPrice
        }
        cart_collection.insert_one(cart_item)
        return jsonify({'success': True, 'message': 'Item added to cart successfully'})
    else:
        return jsonify({'success': False, 'message': 'User not logged in'})

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    if 'username' in session:
        username = session['username']
        
        # Retrieve JSON data from request
        data = request.json
        _id = data.get('id')
        quantity = data.get('quantity')

        # Check if all required keys are present
        if _id is None or quantity is None:
            return jsonify({'success': False, 'message': 'Missing form data'})

        # Update the quantity of the item in the cart
        cart_collection.update_one({'_id': ObjectId(_id), 'username': username}, {'$set': {'quantity': quantity}})
        return jsonify({'success': True, 'message': 'Item quantity updated in cart'})
    else:
        return jsonify({'success': False, 'message': 'User not logged in'})

@app.route('/delete_productcart', methods=['POST'])
def delete_productcart():
    if 'username' in session:
        username = session['username']
        
        # Retrieve JSON data from request
        data = request.json
        _id = data.get('id')

        # Check if all required keys are present
        if _id is None:
            return jsonify({'success': False, 'message': 'Missing form data'})

        # Delete the item from the cart
        cart_collection.delete_one({'_id': ObjectId(_id), 'username': username})
        return jsonify({'success': True, 'message': 'Item deleted from cart'})
    else:
        return jsonify({'success': False, 'message': 'User not logged in'})

@app.route('/view_customers')
def index():
    return render_template('admin_customers.html')
@app.route('/users')
def get_users():
    users = list(users_collection.find())
    for user in users:
        user['_id'] = str(user['_id'])
    return jsonify({'users': users})
@app.route('/user_details', methods=['GET'])
def get_user_details():
    if 'username' in session:
        username = session['username']
        user = users_collection.find_one({'username': username}, {'_id': 0})  # Exclude _id field from the result
        if user:
            return render_template('user_details.html', user=user)
        else:
            return jsonify({'success': False, 'message': 'User not found'}), 404
    else:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401


@app.route('/cart')
def cart():
    if 'username' in session:
        username = session['username']
        # Retrieve cart items for the logged-in user
        cart_items = list(cart_collection.find({'username': username}))

        # Calculate item total, estimated tax, and subtotal
        item_total = Decimal(0)
        for item in cart_items:
            item_price_str = item.get('productPrice', '0').replace('$', '')  # Remove the dollar sign
            try:
                item_price = Decimal(item_price_str)
            except decimal.InvalidOperation as e:
                print(f"Error converting '{item_price_str}' to Decimal: {e}")
                continue
            
            item_quantity_str = item.get('quantity', '0')
            try:
                item_quantity = Decimal(item_quantity_str)
            except decimal.InvalidOperation as e:
                print(f"Error converting '{item_quantity_str}' to Decimal: {e}")
                continue
            
            print(f"Item price: {item_price}, Item quantity: {item_quantity}")  # Add this line for debugging
            item_total += item_price * item_quantity
        
        est_tax = item_total * Decimal('0.045')  # 4.5% tax rate
        subtotal = item_total + est_tax

        return render_template('cart.html', cart_items=cart_items, item_total=item_total, est_tax=est_tax, subtotal=subtotal)
    else:
        # User is not logged in, handle accordingly
        return redirect(url_for('login'))  # Redirect to login page

# @app.route('/cart')
# def cart():
#     if 'username' in session:  # Check if user is logged in
#         username = session['username']
#         # Retrieve cart items for the logged-in user
#         cart_items = cart_collection.find({'username': username})
#         return render_template('cart.html', cart_items=cart_items)
#     else:
#         # User is not logged in, handle accordingly
#         return redirect(url_for('login'))  # Redirect to login page

# @app.route('/cart')
# def view_cart():
#     cart_items = list(db.cart.find())
#     return render_template('cart.html', cart_items=cart_items)

@app.route('/')
def home():
    return render_template('login.html')
@app.route('/orderplaced')
def orderplaced():
    # Get the username from the session
    username = session.get('username')

    # Fetch data based on the logged-in username
    data = deliveries_collection.find_one({"username": username})

    if data:
        return render_template('order_status.html', 
                               products=data.get("products", []),
                               deliveryOption=data.get("deliveryOption", ""),
                               paymentOption=data.get("paymentOption", ""),
                               deliveryAddress=data.get("deliveryAddress", ""),
                               deliveryMobile=data.get("deliveryMobile", ""),
                               productPrice=data.get("productPrice", ""),
                               expectedDelivery=data.get("expectedDelivery", ""),
                               username=data.get("username", ""))
    else:
        return "No order found for this user."

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form['username']
#     password = request.form['password']
#     user = users_collection.find_one({'username': username, 'password': password})
#     if user:
#         return jsonify({'success': True, 'message': 'Login successful'})
#     else:
#         return redirect('/signup')  # Redirect to signup page if user doesn't exist
    


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        contactno = request.form['contactno']
        address= request.form['address']
        user = users_collection.find_one({'username': username})
        if user:
            return jsonify({'success': False, 'message': 'Username already exists'})
        else:
            new_user = {
                'firstname': firstname,
                'lastname': lastname,
                'username': username,
                'password': password,
                'contactno': contactno,
                'address': address
            }
            users_collection.insert_one(new_user)
            return jsonify({'success': True, 'message': 'User created successfully'})
    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)
