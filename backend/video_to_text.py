from flask import Flask, request, jsonify
import cv2
import os
import numpy as np
import mediapipe as mp
import tensorflow as tf

app = Flask(__name__)

# Load trained model
model = tf.keras.models.load_model("models/sign_language_model.h5")

# MediaPipe Hands for gesture tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Define function to process video frames
def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    sentence = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert frame to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                keypoints = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
                keypoints = np.expand_dims(keypoints, axis=0)

                # Predict sign using trained model
                prediction = model.predict(keypoints)
                predicted_class = np.argmax(prediction)

                # Convert gesture class to word (assuming a predefined dictionary)
                gesture_dict = {0: "Hello", 1: "How", 2: "Are", 3: "You"}  # Expand this
                if predicted_class in gesture_dict:
                    sentence.append(gesture_dict[predicted_class])

        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    cap.release()
    
    return " ".join(sentence)

@app.route("/video_to_text", methods=["POST"])
def video_to_text():
    if "video" not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    video_file = request.files["video"]
    video_path = os.path.join("uploads", video_file.filename)
    video_file.save(video_path)

    text_output = process_video(video_path)

    return jsonify({"text": text_output})

if __name__ == "__main__":
    app.run(debug=True)
