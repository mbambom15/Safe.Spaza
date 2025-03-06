from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import winsound
import threading
import datetime

app = Flask(__name__)


scanned_items = []

last_scanned_barcode = None

def beep():
    """Generate a beep sound on Windows."""
    frequency = 1000  
    duration = 200  
    winsound.Beep(frequency, duration)

def generate_frames():
    """Capture frames from webcam and detect barcodes."""
    global last_scanned_barcode
    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        for barcode in decode(frame):
            barcode_data = barcode.data.decode("utf-8")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

           
            last_scanned_barcode = barcode_data
            cap.release()

      
            scanned_items.append({
                "barcode": barcode_data,
                "item_name": "Enter Item Name",
                "expiry_date": None,
                "timestamp": timestamp
            })
            print(f"Scanned: {barcode_data} at {timestamp}")

        
            threading.Thread(target=beep).start()

            points = np.array(barcode.polygon, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], True, (0, 255, 0), 3)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/')
def welcome():
    """Render the welcome page."""
    return render_template('welcome.html')

@app.route('/scanner')
def scanner():
    """Render the scanning page."""
    return render_template('scan.html')

@app.route('/input/<barcode>')
def input_page(barcode):
    """Render the item input page."""
    return render_template('input.html', barcode=barcode)

@app.route('/video_feed')
def video_feed():
    """Stream webcam video feed."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/check_barcode')
def check_barcode():
    """Check if a barcode has been scanned."""
    global last_scanned_barcode
    barcode = last_scanned_barcode
    last_scanned_barcode = None 
    return jsonify({"barcode": barcode})

@app.route('/get_scanned_items')
def get_scanned_items():
    """Return all scanned items (including duplicates)."""
    return jsonify(scanned_items)

@app.route('/update_item', methods=['POST'])
def update_item():
    """Update the item name and expiry date for a scanned barcode."""
    data = request.json
    barcode = data.get("barcode")
    new_name = data.get("item_name")
    new_expiry = data.get("expiry_date")

    for item in scanned_items:
        if item["barcode"] == barcode:
            item["item_name"] = new_name
            item["expiry_date"] = new_expiry

    return jsonify({"message": f"Updated barcode {barcode} to {new_name} with expiry date {new_expiry}!"})

if __name__ == '__main__':
    app.run(debug=True)
