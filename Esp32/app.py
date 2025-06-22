import cv2
import mediapipe as mp
import math
import serial
import time
import numpy as np

esp32_port = "COM4"  # Change to your ESP32 COM port
baud_rate = 115200

# Open Serial Connection
ser = serial.Serial(esp32_port, baud_rate, timeout=1)
time.sleep(2)  # Wait for ESP32 to initialize

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def send_angle(angle): 
    ser.write(f"{angle}\n".encode())  # Send angle with newline
    print(f"Sent Angle: {angle}")
    time.sleep(0.1)  # Wait for ESP32 to process

# Function to calculate the angle between two vectors
def calculate_angle(p1, p2, p3):
    v1 = np.array([p2[0] - p1[0], p2[1] - p1[1]])  # Vector from p1 to p2
    v2 = np.array([p3[0] - p1[0], p3[1] - p1[1]])  # Vector from p1 to p3

    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)

    angle_rad = np.arccos(dot_product / (magnitude_v1 * magnitude_v2))  # Angle in radians
    angle_deg = np.degrees(angle_rad)  # Convert to degrees
    
    return angle_deg

cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw hand landmarks
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lmList = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                # Calculate angle between thumb and index finger (landmarks 4, 5, and 8)
                thumb_tip = (lmList[4][1], lmList[4][2])  # Thumb tip
                index_base = (lmList[5][1], lmList[5][2])  # Index finger base
                index_tip = (lmList[8][1], lmList[8][2])  # Index finger tip

                # Calculate the angle between the thumb and index finger
                angle = calculate_angle(thumb_tip, index_base, index_tip)
                angle = int(angle)  # Convert to integer for better readability
                
                # Send the calculated angle to the ESP32
                send_angle(angle)

                # Display angle on the video feed
                cv2.putText(image, f"Angle: {angle} deg", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Draw the landmarks
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow('Hand Gesture Control', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

ser.close()
