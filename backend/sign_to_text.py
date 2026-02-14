# app = Flask(__name__, template_folder="../templates")   # Adjust the path

import os
import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import pyttsx3
import threading
import time
from flask import Flask, render_template, Response, redirect, send_from_directory, url_for
from collections import deque, Counter

# Load pre-trained model
# model = tf.keras.models.load_model("models/sign_language_model.h5")
model = tf.keras.models.load_model("models/landmark_model.h5")

# # Print model summary
# model.summary()
input_shape = model.input_shape
print("Model Input Shape:", input_shape)

# MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Text-to-Speech
engine = pyttsx3.init()

# Define Labels (Modify based on your model)
# sign_labels = ["hello", "yes", "no", "thank_you", "please"]
sign_labels = ["B","C","W","hello", "i_love_you", "love","no", "please","thank_you","yes"]

# Flask App
# app = Flask(__name__, static_folder='static')
app = Flask(__name__, 
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../templates"))
           )

# Initialize Video Capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Global Variables
sentence = []  # Stores detected words dynamically
last_word = None  # Tracks last detected word
last_detected_time = 0  # Timestamp to avoid duplicate words
word_delay = 5  # Time delay to avoid rapid duplicate word detection
predictions_window = deque(maxlen=15)   # Number of frames to track
# CONFIRMATION_THRESHOLD = 10             # How many times a word must repeat
# CONFIDENCE_THRESHOLD = 0.85             # Confidence required to accept prediction


def speak_text(text):
    """Function to speak the detected text (Optional)."""
    print(f"🔊 Speaking: {text}")
    # Implement text-to-speech here (e.g., pyttsx3)


def process_frame(frame):
    """Detects hand gestures and builds a sentence dynamically."""
    global sentence, last_word, last_detected_time

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract hand landmarks
            landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
            
            # Ensure the landmarks are the right shape
            if landmarks.shape[0] != model.input_shape[1]:
                return "Error: Invalid input shape"

            landmarks = np.expand_dims(landmarks, axis=0)

            # Predict gesture
            with tf.device("/CPU:0"):
                prediction = model.predict(landmarks, verbose=0)

            predicted_class = np.argmax(prediction)
            text = sign_labels[predicted_class]

            # ✅ Debugging statements
            print("Hand detected!")
            print(f"🔍 Model Prediction: {prediction}")
            print(f"🎯 Predicted Class Index: {predicted_class}")
            print(f"📝 Detected Word: {text}")

            # Avoid duplicate words within a short time window
            current_time = time.time()
            if text != last_word or (current_time - last_detected_time) > word_delay:
                sentence.append(text)
                last_word = text
                last_detected_time = current_time

                # Run text-to-speech in a separate thread
                threading.Thread(target=speak_text, args=(text,), daemon=True).start()

    return " ".join(sentence)


# def generate_frames():
#     """Generates video frames with real-time text overlay."""
#     while cap.isOpened():
#         success, frame = cap.read()
#         if not success:
#             print("⚠️ ERROR: Cannot read frame from webcam!")
#             break

#         text = process_frame(frame)  # Process frame to get recognized text

#         # Overlay detected text on frame
#         cv2.putText(frame, f"Detected: {text}", (30, 50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#         # Encode frame as JPEG
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

#     cap.release()


def generate_frames():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        success, frame = cap.read()
        if not success:
            print("⚠️ ERROR: Cannot read frame from webcam!")
            break

        text = process_frame(frame)

        # Overlay detected text
        cv2.putText(frame, f"Detected: {text}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()



@app.route('/')
def index():
    return render_template('sign_to_text.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/back')
def back_to_dashboard():
    return redirect(url_for('dashboard'))

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_text')
def get_text():
    """Returns the detected text as JSON to the frontend."""
    global sentence

    if not sentence:  # If no sign has been recognized yet
        detected_text = "Waiting for signs..."
    else:
        detected_text = " ".join(sentence)

    print(f"📢 Sending to frontend: {detected_text}")  # Debugging

    return detected_text, 200, {'Content-Type': 'text/plain'}  # Ensure plain text response


@app.route('/clear_text', methods=['POST'])
def clear_text():
    """Clears the detected sentence when the user clicks 'Clear Text'."""
    global sentence
    sentence = []  # Reset the sentence list
    return '', 204  # Respond with "No Content"


