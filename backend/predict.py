import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load the trained model
model = tf.keras.models.load_model("sign_language_model.h5")

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

@app.route("/predict", methods=["POST"])
def predict_sign():
    file = request.files["video"]
    cap = cv2.VideoCapture(file)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process frame for landmarks
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
                prediction = model.predict(np.expand_dims(landmarks, axis=0))
                label = np.argmax(prediction)

                return jsonify({"text": label})

    cap.release()
    return jsonify({"text": "No sign detected."})

if __name__ == "__main__":
    app.run(debug=True)
