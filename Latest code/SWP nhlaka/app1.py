from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder='temp')

def create_connection():
    return mysql.connector.connect(
        host="10.2.37.86",      
        user="lisa",    
        password="1234",
        database="spaza_safe"      
    )

# Global variables for barcode scanning
scanned_data = None
camera_active = False
cap = None

def generate_frames():
    global scanned_data, camera_active, cap

    if cap is None:
        cap = cv2.VideoCapture(0)
        cap.set(3, 640)  # Set width
        cap.set(4, 480)  # Set height

    while True:
        if camera_active:
            success, img = cap.read()
            if not success:
                break
            else:
                # Decode barcodes in the current frame
                for barcode in decode(img):
                    scanned_data = barcode.data.decode('utf-8')  # Store scanned data
                    camera_active = False  # Stop camera after scanning

                    # Draw bounding box around barcode
                    pts = np.array([barcode.polygon], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(img, [pts], True, (255, 0, 255), 5)

                    # Display barcode text on frame
                    x, y, _, _ = barcode.rect
                    cv2.putText(img, scanned_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

                _, buffer = cv2.imencode('.jpg', img)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # When camera is inactive, display a paused frame
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank_frame, "Camera Paused", (220, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', blank_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
@app.route('/update_password_owner', methods=['GET', 'POST'])
def update_password_owner():
    if request.method == 'POST':
        data = request.form
        username = data.get('owner_name')
        new_password = data.get('new_password')

        if not all([username, new_password]):
            return redirect(url_for('login_spazaOwner', message="Username and new password are required"))

        if len(new_password) > 15:
            return redirect(url_for('login_spazaOwner', message="Password must be 15 characters or less"))

        connection = None
        try:
            connection = create_connection()
            cursor = connection.cursor()

            query = "UPDATE Spaza_Owner SET opassword = %s WHERE oname = %s"
            cursor.execute(query, (new_password, username))
            connection.commit()

            if cursor.rowcount == 0:
                return redirect(url_for('login_spazaOwner', message="Shop owner not found"))

            return redirect(url_for('login_spazaOwner', message="Password updated successfully"))

        except Error as e:
            if connection:
                connection.rollback()
            return redirect(url_for('login_spazaOwner', message=f"Error: {str(e)}"))

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('update_passwordo.html')


@app.route('/update_password_manufacturer', methods=['GET', 'POST'])
def update_password_manufacturer():
            if request.method == 'POST':
                data = request.form
                license_key = data.get('license_key')
                new_password = data.get('new_password')

                if not all([license_key, new_password]):
                    return redirect(url_for('login_manufacturer', message="License key and new password are required"))

                if len(new_password) > 15:
                    return redirect(url_for('login_manufacturer', message="Password must be 15 characters or less"))

                connection = None
                try:
                    connection = create_connection()
                    cursor = connection.cursor()

                    query = "UPDATE Manufacturer SET mpassword = %s WHERE license_key = %s"
                    cursor.execute(query, (new_password, license_key))
                    connection.commit()

                    if cursor.rowcount == 0:
                        return redirect(url_for('login_manufacturer', message="Manufacturer not found"))

                    return redirect(url_for('login_manufacturer', message="Password updated successfully"))

                except Error as e:
                    if connection:
                        connection.rollback()
                    return redirect(url_for('login_manufacturer', message=f"Error: {str(e)}"))

                finally:
                    if connection and connection.is_connected():
                        cursor.close()
                        connection.close()

            return render_template('update_password.html')

@app.route('/')
def home():
    
    return redirect(url_for('spazalogin'))

@app.route('/spazalogin')
def spazalogin():
    return render_template('spazalogin.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/login_manufacturer', methods=['GET', 'POST'])
def login_manufacturer():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not all([username, password]):
            return jsonify({"success": False, "message": "All fields are required"}), 400

        connection = None
        try:
            connection = create_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT license_key, company_name FROM Manufacturer
                WHERE license_key = %s AND mpassword = %s
            """, (username, password))

            manufacturer = cursor.fetchone()

            if manufacturer:
                return jsonify({
                    "success": True,
                    "message": "Login successful",
                    "redirect": url_for('manudashboard'),
                    "user": {
                        "id": manufacturer['license_key'],
                        "name": manufacturer['company_name']
                    }
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Invalid credentials"
                }), 401

        except Error as e:
            return jsonify({
                "success": False,
                "message": f"Database error: {str(e)}"
            }), 500
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('login_manufacturer.html')

@app.route('/signup_manufacturer', methods=['GET', 'POST'])
def signup_manufacturer():
    if request.method == 'POST':
        # Get form data
        license_key = request.form.get('license_key')
        company_name = request.form.get('company_name')
        address = request.form.get('address')
        location = request.form.get('location')
        password = request.form.get('password')

        # Validate required fields
        if not all([license_key, company_name, address, location, password]):
            return jsonify({
                "success": False,
                "message": "All fields are required"
            }), 400

        connection = None
        try:
            connection = create_connection()
            cursor = connection.cursor()

            # Check if license key already exists
            cursor.execute("SELECT license_key FROM Manufacturer WHERE license_key = %s", (license_key,))
            if cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "License key already registered"
                }), 400

            # Insert new manufacturer
            query = """
                INSERT INTO Manufacturer (license_key, company_name, address, location, mpassword)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (license_key, company_name, address, location, password))
            connection.commit()

            return jsonify({
                "success": True,
                "message": "Registration successful",
                "redirect": url_for('login_manufacturer')
            })

        except Error as e:
            if connection:
                connection.rollback()
            return jsonify({
                "success": False,
                "message": f"Database error: {str(e)}"
            }), 500

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    # If GET, just show the form
    return render_template('signup_manufacturer.html')

@app.route('/signup_spazaOwner', methods=['GET', 'POST'])
def signup_spazaOwner():
    if request.method == 'POST':
        # Get form data
        oname = request.form.get('oname')
        opassword = request.form.get('opassword')
        phone_number = request.form.get('phone_number')
        business_name = request.form.get('business_name')
        business_reg_number = request.form.get('business_reg_number')

        # Validate required fields
        if not all([oname, opassword, phone_number, business_name]):
            return jsonify({
                "success": False,
                "message": "All required fields must be filled"
            }), 400

        # Validate password length
        if len(opassword) > 15:
            return jsonify({
                "success": False,
                "message": "Password must be 15 characters or less"
            }), 400

        connection = None
        try:
            connection = create_connection()
            cursor = connection.cursor()

            # Check if business name already exists
            cursor.execute("SELECT business_name FROM Spaza_Owner WHERE business_name = %s", (business_name,))
            if cursor.fetchone():
                return jsonify({
                    "success": False,
                    "message": "Business name already exists"
                }), 400

            # Insert new shop owner
            query = """
                INSERT INTO Spaza_Owner (oname, opassword, phone_number, business_name, business_reg_number)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (oname, opassword, phone_number, business_name, business_reg_number))
            connection.commit()

            return jsonify({
                "success": True,
                "message": "Registration successful! Redirecting to login...",
                "redirect": url_for('login_spazaOwner')
            })

        except Error as e:
            if connection:
                connection.rollback()
            return jsonify({
                "success": False,
                "message": f"Database error: {str(e)}"
            }), 500

        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()

    return render_template('signup_spazaOwner.html')

@app.route('/manudashboard')
def manudashboard():
    return render_template('manudashboard.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.json
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor()

        # Check if barcode already exists
        cursor.execute("SELECT prod_barcode FROM Product WHERE prod_barcode = %s", (data['barcode'],))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Product with this barcode already exists"}), 400

        query = """
        INSERT INTO Product (prod_barcode, prod_name, prod_price, prod_expiry_date, prod_manu_date, license_key)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data['barcode'],
            data['name'],
            data['price'],
            data['expiry_date'],
            data['manufacture_date'],
            data['manufacturer_id']
        ))
        connection.commit()
        return jsonify({"success": True, "message": "Product added successfully"})

    except Error as e:
        if connection:
            connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/update_product', methods=['PUT'])
def update_product():
    data = request.json
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        query = """
            UPDATE Product 
            SET prod_name = %s, prod_price = %s, prod_expiry_date = %s, prod_manu_date = %s
            WHERE prod_barcode = %s AND license_key = %s
        """
        cursor.execute(query, (
            data['name'],
            data['price'],
            data['expiry_date'],
            data['manufacture_date'],
            data['barcode'],
            data['manufacturer_id']
        ))
        connection.commit()
        
        return jsonify({"success": True, "message": "Product updated successfully"})
        
    except Error as e:
        if connection:
            connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/delete_product/<barcode>', methods=['DELETE'])
def delete_product(barcode):
    # Get manufacturer_id from session or request
    manufacturer_id = request.args.get('manufacturer_id')
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        query = "DELETE FROM Product WHERE prod_barcode = %s AND license_key = %s"
        cursor.execute(query, (barcode, manufacturer_id))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Product not found or not owned by manufacturer"}), 404
        
        return jsonify({"success": True, "message": "Product deleted successfully"})
        
    except Error as e:
        if connection:
            connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/get_products')
def get_products():
    manufacturer_id = request.args.get('manufacturer_id')
    
    if not manufacturer_id:
        return jsonify({"success": False, "message": "Manufacturer ID is required"}), 400

    # Convert manufacturer_id to integer
    try:
        manufacturer_id_int = int(manufacturer_id)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid manufacturer ID format"}), 400
    
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verify the manufacturer exists 
        cursor.execute("SELECT license_key FROM Manufacturer WHERE license_key = %s", (manufacturer_id_int,))
        if not cursor.fetchone():
            return jsonify({"success": False, "message": "Invalid manufacturer ID"}), 401
        
        # Get only products belonging to this manufacturer
        query = "SELECT * FROM Product WHERE license_key = %s"
        cursor.execute(query, (manufacturer_id_int,))
        products = cursor.fetchall()
        
        return jsonify(products)
        
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/get_product')
def get_product():
    barcode = request.args.get('barcode')
    manufacturer_id = request.args.get('manufacturer_id')
    
    if not all([barcode, manufacturer_id]):
        return jsonify({"success": False, "message": "Barcode and manufacturer ID are required"}), 400
    
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM Product WHERE prod_barcode = %s AND license_key = %s"
        cursor.execute(query, (barcode, manufacturer_id))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({"success": False, "message": "Product not found"}), 404
        
        return jsonify(product)
        
    except Error as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/order_stock')
def order_stock():
    return render_template('order_stock.html')


@app.route('/shopowner')
def shopowner():
    return render_template('shopowner.html')

@app.route('/add_to_inventory', methods=['POST'])
def add_to_inventory():
    data = request.json
    # Expected data: registration_no (spaza shop id), prod_barcode, shop_price, stock_quantity
    registration_no = data.get('registration_no')
    prod_barcode = data.get('prod_barcode')
    shop_price = data.get('shop_price')
    stock_quantity = data.get('stock_quantity')
    
    if not all([registration_no, prod_barcode, shop_price, stock_quantity]):
        return jsonify({"success": False, "message": "All fields are required"}), 400
    
    connection = None
    try:
        connection = create_connection()
        cursor = connection.cursor()
        
        # Check if the inventory record already exists for this shop and product
        cursor.execute("""
            SELECT inventory_id FROM Shop_Inventory
            WHERE registration_no = %s AND prod_barcode = %s
        """, (registration_no, prod_barcode))
        result = cursor.fetchone()
        
        if result:
            # If exists, update the stock and shop price (or you might want to add to stock)
            update_query = """
                UPDATE Shop_Inventory
                SET shop_price = %s, stock_quantity = %s
                WHERE registration_no = %s AND prod_barcode = %s
            """
            cursor.execute(update_query, (shop_price, stock_quantity, registration_no, prod_barcode))
        else:
            # Insert a new record into the inventory
            insert_query = """
                INSERT INTO Shop_Inventory (registration_no, prod_barcode, shop_price, stock_quantity)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (registration_no, prod_barcode, shop_price, stock_quantity))
        
        connection.commit()
        return jsonify({"success": True, "message": "Inventory updated successfully"})
    except Error as e:
        if connection:
            connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# This route queries MySQL based on the scanned barcode
@app.route('/scan_barcode')
def scan_barcode():
    global scanned_data
    barcode = scanned_data

    if not barcode:
        return jsonify({"barcode": "No barcode scanned yet"})

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM Product WHERE prod_barcode = %s"
        cursor.execute(query, (barcode,))
        result = cursor.fetchone()
        
        if result:
            # Return all product information as JSON
            return jsonify(result)
        else:
            return jsonify({"barcode": barcode, "message": "No product found for this barcode."})
    
    except Error as e:
        print(f"Database error: {e}")
        return jsonify({"message": "Database connection error", "error": str(e)})
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/start_camera')
def start_camera():
    global camera_active, scanned_data
    camera_active = True
    scanned_data = None
    return jsonify({"status": "Camera started"})

if __name__ == "__main__":
    app.run(debug=True)
