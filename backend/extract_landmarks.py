import subprocess
import cv2
import numpy as np
import mediapipe as mp
import os

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.5)

# Folder containing sign images
dataset_folder = "datasets/sign_images"
labels = []
landmarks_data = []

# Process each image
for label in os.listdir(dataset_folder):
    label_folder = os.path.join(dataset_folder, label)
    if not os.path.isdir(label_folder):
        continue

    for img_name in os.listdir(label_folder):
        img_path = os.path.join(label_folder, img_name)
        image = cv2.imread(img_path)

        if image is None:
            continue

        # Convert to RGB and process with MediaPipe
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(image_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark]).flatten()
                if len(landmarks) == 63:  # Ensure correct size
                    landmarks_data.append(landmarks)
                    labels.append(label)

# Convert to NumPy arrays
x_train = np.array(landmarks_data, dtype=np.float32)
y_train = np.array(labels)

# Save extracted landmarks
np.save("x_train.npy", x_train)
np.save("y_train.npy", y_train)
print("✅ Landmarks extracted and saved!")

# ✅ Trigger the Training Script
print("🚀 Starting model training...")
# subprocess.run(["python", "backend/train_landmark_model.py"])
subprocess.Popen(["python", "backend/train_landmark_model.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)
