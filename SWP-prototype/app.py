from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder='temp')

def create_connection():
    return mysql.connector.connect(
        host="localhost",       
        user="mbambo",    
        password="Mbambo1307#a",
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
                    x, y, w, h = barcode.rect
                    cv2.putText(img, scanned_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

                ret, buffer = cv2.imencode('.jpg', img)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # When camera is inactive, display a paused frame
            blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank_frame, "Camera Paused", (220, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', blank_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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

@app.route('/login_manufacturer')
def login_manufacturer():
    return render_template('login_manufacturer.html')

@app.route('/login_spazaOwner')
def login_spazaOwner():
    return render_template('login_spazaOwner.html')

@app.route('/signup_manufacturer')
def signup_manufacturer():
    return render_template('signup_manufacturer.html')

@app.route('/signup_spazaOwner')
def signup_spazaOwner():
    return render_template('signup_spazaOwner.html')

@app.route('/manudashboard')
def manudashboard():
    return render_template('manudashboard.html')

@app.route('/shopowner')
def shopowner():
    return render_template('shopowner.html')

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
