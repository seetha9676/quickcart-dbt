import decimal
import os
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from mysql.connector import connect, Error
from decimal import Decimal
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'whekjrherlwjerlwjerlkwejrkwensmend'

# MySQL Connection Configuration
db_config = {
    'host': os.getenv('DB_HOST', 'sql3.freesqldatabase.com'),
    'user': os.getenv('DB_USER', 'sql3751732'),
    'password': os.getenv('DB_PASSWORD', 'MAjpadWRhi'),
    'database': os.getenv('DB_NAME', 'sql3751732'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def get_db_connection():
    return connect(**db_config)

@app.route('/home')
def main():
    return render_template('home.html')

@app.route('/users')
def user():
    return render_template('admin_customers.html')
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
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE category = %s", (category,))
        products = cursor.fetchall()
        return render_template('products.html', products=products)
    finally:
        cursor.close()
        connection.close()
        
@app.route('/users_detail')
def users():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                `_id`, 
                `firstname`, 
                `lastname`, 
                `username`, 
                `contactno`, 
                `address`
            FROM `customer`;
        """)
        customers = cursor.fetchall()
        return jsonify({'users': customers})
    finally:
        cursor.close()
        connection.close()


# @app.route('/cancellation_details')
# def cancellation_details():
#     try:
#         connection = get_db_connection()
#         cursor = connection.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT 
#                 `cancellation`.`_id`,
#                 `cancellation`.`username`,
#                 `cancellation`.`products.0.productName` AS product0_name,
#                 `cancellation`.`products.0.size` AS product0_size,
#                 `cancellation`.`products.0.quantity` AS product0_quantity,
#                 `cancellation`.`products.0.price` AS product0_price,
#                 `cancellation`.`products.1.productName` AS product1_name,
#                 `cancellation`.`products.1.size` AS product1_size,
#                 `cancellation`.`products.1.quantity` AS product1_quantity,
#                 `cancellation`.`products.1.price` AS product1_price,
#                 `cancellation`.`reason`,
#                 `cancellation`.`comment`
#             FROM `cancellation`
#         """)
#         cancelled_orders = cursor.fetchall()
        
#         # Debugging: Print the data to confirm it is fetched
#         print(cancelled_orders)

#         return render_template('cancelled_user.html', cancelled_orders=cancelled_orders)
#     finally:
#         cursor.close()
#         connection.close()
# @app.route('/cancellation_details')
# def cancellation_details():
#     try:
#         connection = get_db_connection()
#         cursor = connection.cursor(dictionary=True)
#         cursor.execute("""
#             SELECT 
#                 `_id`,
#                 `username`,
#                 `comment`,
#                 `products.0.productName` AS product0_name,
#                 `products.0.size` AS product0_size,
#                 `products.0.quantity` AS product0_quantity,
#                 `products.0.price` AS product0_price,
#                 `products.1.productName` AS product1_name,
#                 `products.1.size` AS product1_size,
#                 `products.1.quantity` AS product1_quantity,
#                 `products.1.price` AS product1_price,
#                 `reason`
#             FROM `cancellation`;
#         """)
#         cancelled_orders = cursor.fetchall()
#         return render_template('cancelled_user.html', cancelled_orders=cancelled_orders)
#     finally:
#         cursor.close()
#         connection.close()
@app.route('/user_details')
def user_details():
    if 'username' not in session:
        return redirect('/login')  # Redirect to login if the user is not logged in

    username = session['username']
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Fetch user details
        cursor.execute("""
            SELECT 
                `firstname`, 
                `lastname`, 
                `username`, 
                `contactno`, 
                `address` 
            FROM `customer` 
            WHERE `username` = %s
        """, (username,))
        user = cursor.fetchone()

        if not user:
            return "User not found", 404

        return render_template('user_details.html', user=user)

    except Exception as e:
        print(f"Error fetching user details: {e}")
        return "An error occurred while fetching user details.", 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/cancellation_details')
def cancellation_details():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                `_id`,
                `username`,
                `comment`,
                `products.0.productName` AS product0_name,
                `products.0.size` AS product0_size,
                `products.0.quantity` AS product0_quantity,
                `products.0.price` AS product0_price,
                `products.1.productName` AS product1_name,
                `products.1.size` AS product1_size,
                `products.1.quantity` AS product1_quantity,
                `products.1.price` AS product1_price,
                `reason`
            FROM `cancellation`;
        """)
        cancelled_orders = cursor.fetchall()
        return render_template('cancelled_user.html', cancelled_orders=cancelled_orders)
    finally:
        cursor.close()
        connection.close()

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check if admin
        cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['username'] = username
            return redirect('/all_products')

        # Check if regular user
        cursor.execute("SELECT * FROM customer WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            session['username'] = username
            return jsonify({'success': True, 'message': 'Login successful', 'username': username})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    finally:
        cursor.close()
        connection.close()

@app.route('/order')
def order():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Query to fetch only the required columns
        cursor.execute("""
            SELECT username, productId, productName, productSize, quantity, productPrice 
            FROM deliveries
        """)
        orders = cursor.fetchall()
        
        # Pass the result to the template
        return render_template('admin_orders.html', orders=orders)
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return jsonify({'success': False, 'message': 'Error fetching orders'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/all_products')
def all_products():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        return render_template('all_products.html', products=products)
    finally:
        cursor.close()
        connection.close()
def get_db_connection():
    return connect(**db_config)
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    connection = None
    cursor = None
    try:
        # Parse incoming JSON data
        data = request.json
        print("Received Data:", data)  # Debugging: Print the received data

        # Validate required fields
        productid = data.get('productId')  # Fixed variable name to match data.get
        product_name = data.get('productName')
        product_size = data.get('productSize')
        product_price = data.get('productPrice')
        quantity = data.get('quantity')

        if not all([productid, product_name, product_size, product_price, quantity]):
            return jsonify({'success': False, 'message': 'Missing required product data'}), 400

        # Clean and convert product_price
        try:
            product_price = float(product_price.replace('$', '').strip())
            quantity = int(quantity)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid productPrice or quantity'}), 400

        # Retrieve the currently logged-in username from session
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'User is not logged in'}), 401

        username = session['username']

        # Connect to the database and insert data
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO `order` (username, productid, productName, productSize, quantity, productPrice)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (username, productid, product_name, product_size, quantity, product_price)  # Ensure all values match placeholders
        )
        connection.commit()

        # Success response
        return jsonify({'success': True, 'message': 'Product added to order table successfully!'}), 200
    except Exception as e:
        print("Error:", str(e))  # Debugging: Print the error
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    username = session['username']
    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Delete all records for the given username from the `order` table
        cursor.execute("DELETE FROM `order` WHERE username = %s", (username,))
        connection.commit()

        if cursor.rowcount > 0:
            return jsonify({'success': True, 'message': 'Cart cleared successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'No records found to delete'}), 404

    except Exception as e:
        print(f"Error clearing cart: {e}")
        return jsonify({'success': False, 'message': f'Error clearing cart: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/add_product', methods=['POST'])
def add_product():
    product_data = request.form.to_dict()
    print(product_data)
    # Validate productid
    if not product_data.get('productid'):
        return jsonify({'message': 'Product ID is missing'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO products (productname, productid, size, price, type, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                product_data['productname'],
                product_data['productid'],
                product_data['size'],
                product_data['price'],
                product_data['type'],
                product_data['category']
            )
        )
        connection.commit()
        return jsonify({'message': 'Product added successfully'}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Failed to add product'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/delete_product/<product_id>', methods=['GET'])
def delete_product(product_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE productid = %s", (product_id,))
        connection.commit()
        if cursor.rowcount == 1:
            return redirect(url_for('all_products'))
        else:
            return "Product not found", 404
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred", 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/get_product/<string:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM products WHERE productid = %s", (product_id,))
        product = cursor.fetchone()
        if product:
            return jsonify(product), 200
        else:
            return 'Product not found', 404
    except Exception as e:
        print(f"Error: {e}")
        return str(e), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/edit_product/<product_id>', methods=['POST'])
def edit_product(product_id):
    updated_product_data = request.form.to_dict()
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE products SET productname = %s, size = %s, price = %s, type = %s, category = %s WHERE productid = %s",
            (
                updated_product_data['productname'],
                updated_product_data['size'],
                updated_product_data['price'],
                updated_product_data['type'],
                updated_product_data['category'],
                product_id
            )
        )
        connection.commit()
        if cursor.rowcount == 1:
            return 'Product updated successfully', 200
        else:
            return 'Product not found', 404
    except Exception as e:
        print(f"Error: {e}")
        return 'An error occurred', 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

import json
@app.route('/test_query')
def test_query():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                `cancellation`.`_id`,
                `cancellation`.`username`,
                `cancellation`.`products.0.productName` AS product0_name,
                `cancellation`.`products.0.size` AS product0_size,
                `cancellation`.`products.0.quantity` AS product0_quantity,
                `cancellation`.`products.0.price` AS product0_price,
                `cancellation`.`products.1.productName` AS product1_name,
                `cancellation`.`products.1.size` AS product1_size,
                `cancellation`.`products.1.quantity` AS product1_quantity,
                `cancellation`.`products.1.price` AS product1_price,
                `cancellation`.`reason`,
                `cancellation`.`comment`
            FROM `cancellation`
        """)
        result = cursor.fetchall()
        print(result)  # Debugging: Check query result
        return jsonify(result)
    finally:
        cursor.close()
        connection.close()
@app.route('/cart')
def cart():
    if 'username' in session:
        username = session['username']
        try:
            # Connect to the MySQL database
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            # Query to fetch order items for the logged-in user
            cursor.execute("""
                SELECT _id, productid, productName, productSize, quantity, productPrice
                FROM `order`
                WHERE username = %s
            """, (username,))
            order_items = cursor.fetchall()

            # Calculate item total, estimated tax, and subtotal
            item_total = Decimal(0)
            for item in order_items:
                try:
                    item_price = Decimal(item.get('productPrice', 0))
                    item_quantity = Decimal(item.get('quantity', 0))
                    item_total += item_price * item_quantity
                except decimal.InvalidOperation as e:
                    print(f"Error processing item: {e}")
                    continue

            est_tax = item_total * Decimal('0.045')  # 4.5% tax rate
            subtotal = item_total + est_tax

            # Render the cart page
            return render_template('cart.html', cart_items=order_items, item_total=item_total, est_tax=est_tax, subtotal=subtotal)

        except Exception as e:
            print(f"Error fetching cart data: {e}")
            return jsonify({'success': False, 'message': 'Error fetching cart data'})

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        # User is not logged in, redirect to login page
        return redirect(url_for('login'))
@app.route('/delete_productcart', methods=['POST'])
def delete_productcart():
    if 'username' in session:
        username = session['username']

        # Retrieve JSON data from the request
        data = request.json
        order_id = data.get('id')  # Assuming `id` corresponds to `_id` in the `order` table

        if not order_id:
            return jsonify({'success': False, 'message': 'Missing order ID'}), 400

        try:
            # Connect to the MySQL database
            connection = get_db_connection()
            cursor = connection.cursor()

            # Query to delete the order item for the given `_id` and username
            cursor.execute("""
                DELETE FROM `order`
                WHERE _id = %s AND username = %s
            """, (order_id, username))
            connection.commit()

            # Check if any row was deleted
            if cursor.rowcount > 0:
                return jsonify({'success': True, 'message': 'Item deleted from order table'})
            else:
                return jsonify({'success': False, 'message': 'Item not found'}), 404

        except Exception as e:
            print(f"Error deleting order item: {e}")
            return jsonify({'success': False, 'message': 'Error deleting order item'})

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        # User is not logged in
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

@app.route('/cancelled_orders')
def cancelled_orders():
    if 'username' in session:
        username = session['username']
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            
            # SQL query to fetch data from the cancellation table
            query = """
            SELECT 
                `cancellation`.`_id`,
                `cancellation`.`username`,
                `cancellation`.`products.0.productName` AS product0_name,
                `cancellation`.`products.0.size` AS product0_size,
                `cancellation`.`products.0.quantity` AS product0_quantity,
                `cancellation`.`products.0.price` AS product0_price,
                `cancellation`.`products.1.productName` AS product1_name,
                `cancellation`.`products.1.size` AS product1_size,
                `cancellation`.`products.1.quantity` AS product1_quantity,
                `cancellation`.`products.1.price` AS product1_price,
                `cancellation`.`products.2.productName` AS product2_name,
                `cancellation`.`products.2.size` AS product2_size,
                `cancellation`.`products.2.quantity` AS product2_quantity,
                `cancellation`.`products.2.price` AS product2_price,
                `cancellation`.`reason`,
                `cancellation`.`comment`
            FROM `cancellation`
            WHERE `username` = %s
            """
            
            cursor.execute(query, (username,))
            cancelled_orders = cursor.fetchall()

            # Debugging output to verify the data
            print(cancelled_orders)

            return render_template('cancelled_user.html', cancelled_orders=cancelled_orders)
        finally:
            cursor.close()
            connection.close()
    else:
        return "You are not logged in."
@app.route('/place_order', methods=['POST'])
def place_order():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'}), 401

    username = session['username']
    data = request.json

    required_fields = ['deliveryOption', 'paymentOption', 'products']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'message': f'Missing field: {field}'}), 400

    if not isinstance(data['products'], list) or len(data['products']) == 0:
        return jsonify({'success': False, 'message': 'Products should be a non-empty list'}), 400

    for product in data['products']:
        if not all(key in product for key in ['productId', 'productName', 'size', 'quantity', 'price']):
            return jsonify({'success': False, 'message': 'Missing product details in payload'}), 400

    delivery_option = data.get('deliveryOption')
    payment_option = data.get('paymentOption')
    delivery_address = data.get('deliveryAddress', None)
    delivery_mobile = data.get('deliveryMobile', None)
    expected_delivery = data.get('expectedDelivery', None)

    if delivery_option == 'delivery' and not all([delivery_address, delivery_mobile, expected_delivery]):
        return jsonify({'success': False, 'message': 'Missing delivery details'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        for product in data['products']:
            cursor.execute("""
                INSERT INTO deliveries (
                    username, productId, productName, productSize, quantity, productPrice,
                    deliveryOption, paymentOption, deliveryAddress, deliveryMobile, expectedDelivery
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                username, product['productId'], product['productName'], product['size'],
                product['quantity'], product['price'], delivery_option, payment_option,
                delivery_address, delivery_mobile, expected_delivery
            ))
        connection.commit()
        return jsonify({'success': True, 'message': 'Order placed successfully!'}), 200
    except Exception as e:
        print(f"Error placing order: {e}")
        return jsonify({'success': False, 'message': f'Failed to place order: {str(e)}'}), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/orderplaced')
def order_placed():
    if 'username' not in session:
        return redirect('/login')  # Redirect to login if user is not logged in

    username = session['username']

    try:
        # Connect to the database
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch delivery details for the logged-in user
        cursor.execute("SELECT * FROM deliveries WHERE username = %s", (username,))
        orders = cursor.fetchall()

        # Render the order_status.html with the orders data
        return render_template('order_status.html', orders=orders)

    except Exception as e:
        print(f"Error fetching orders: {e}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        # Render the signup form
        return render_template('signup.html')
    elif request.method == 'POST':
        # Handle form submission
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        contactno = request.form['contactno']
        address = request.form['address']
        
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            
            # Check if the username already exists
            cursor.execute("SELECT * FROM customer WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                return jsonify({'success': False, 'message': 'Username already exists'}), 400
            
            # Insert new user into the customer table
            cursor.execute("""
                INSERT INTO customer (firstname, lastname, username, password, contactno, address)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (firstname, lastname, username, password, contactno, address))
            
            connection.commit()
            return jsonify({'success': True, 'message': 'User created successfully!'}), 201
        
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'success': False, 'message': 'An error occurred'}), 500
        
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

@app.route('/')
def home():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
