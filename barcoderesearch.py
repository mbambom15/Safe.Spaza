import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

while True:
    success, img = cap.read()  # Read frame from camera
    
    for barcode in decode(img):
        myData = barcode.data.decode('utf-8')  # Decode barcode data
        print("Scanned Data:", myData)  # Print barcode text
        
        # Ensure barcode has a polygon before processing
        if barcode.polygon:
            pts = np.array([barcode.polygon], np.int32)  # Get barcode corners
            pts = pts.reshape((-1, 1, 2))  # Reshape for OpenCV
            cv2.polylines(img, [pts], True, (255, 0, 255), 5)  # Draw bounding box
        
        # Draw text above barcode
        x, y, w, h = barcode.rect  # Get barcode rectangle
        cv2.putText(img, myData, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

    cv2.imshow('Result', img)  # Display result

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
