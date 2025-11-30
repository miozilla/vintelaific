import cv2

# vehicle detection tool

'''
def count_cars(source, roi=None):
    cap = cv2.VideoCapture(source)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return 0
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cars = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=2.0, minDist=50)  # placeholder; swap with cascade/YOLO
    return 0 if cars is None else min(len(cars[0]), 10)
'''

# Load pretrained models (replace with YOLOv8 or Haar cascades for demo)
car_cascade = cv2.CascadeClassifier("cars.xml")
ambulance_cascade = cv2.CascadeClassifier("ambulance.xml")  # custom trained cascade

def detect_vehicles(source, roi=None):
    cap = cv2.VideoCapture(source)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return {"car_count": [], "emergency_detected": False}

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect cars
    cars = car_cascade.detectMultiScale(gray, 1.1, 2)
    car_count = [len(cars)]  # simple count per lane

    # Detect ambulances (emergency vehicles)
    ambulances = ambulance_cascade.detectMultiScale(gray, 1.1, 2)
    emergency_detected = len(ambulances) > 0

    return {"car_count": car_count, "emergency_detected": emergency_detected}
