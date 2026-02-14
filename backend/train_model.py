
# modified train_model.py
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import os

# Set dataset path
# dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"datasets", "sign_images")
dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "sign_images")


# Get class labels (folder names)
sign_labels = sorted(os.listdir(dataset_path))  # ["Hello", "No", "Yes"]
num_classes = len(sign_labels)
print(f"Detected classes: {sign_labels}")

# Image preprocessing parameters
IMG_SIZE = 64  # Resize images to 64x64 pixels
x_train = []
y_train = []

# Load images and labels
for label_idx, label in enumerate(sign_labels):
    label_folder = os.path.join(dataset_path, label)

    if not os.path.exists(label_folder):  # Check if folder exists
        print(f"⚠ Warning: Folder not found - {label_folder}")
        continue

    images = os.listdir(label_folder)
    if len(images) == 0:
        print(f"⚠ Warning: No images found in {label_folder}")
        continue

    for img_name in images:
        img_path = os.path.join(label_folder, img_name)

        try:
            img = load_img(img_path, target_size=(IMG_SIZE, IMG_SIZE))  # Load image
            img_array = img_to_array(img) / 255.0  # Convert to array & normalize
            
            x_train.append(img_array)
            y_train.append(label_idx)  # Assign numerical label

        except Exception as e:
            print(f" Error loading {img_path}: {e}")

# Convert lists to NumPy arrays
x_train = np.array(x_train)
y_train = np.array(y_train, dtype=np.int32).flatten()  # Ensure it's 1D

# Print shape to confirm images are loaded
print(f" Final x_train shape: {x_train.shape}")
print(f" Final y_train shape: {y_train.shape}")


# Convert labels to categorical

# Convert labels to one-hot encoding
num_classes = len(sign_labels)  # Automatically detect number of classes
y_train = to_categorical(y_train, num_classes)
print(f"🟢 Corrected y_train shape: {y_train.shape}")  # Should be (samples, num_classes)


# y_train = to_categorical(y_train, num_classes=num_classes)

print(f"Final x_train shape: {x_train.shape}")
print(f"Final y_train shape: {y_train.shape}")

# Define the model
model = Sequential([
    Flatten(input_shape=(IMG_SIZE, IMG_SIZE, 3)),  # Adjust input shape for images
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(num_classes, activation='softmax')  # Output layer matches number of classes
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

if x_train.shape[0] == 0 or y_train.shape[0] == 0:
    raise ValueError("Error: No data found. Please check dataset path and image loading.")


# Train the model
# Ensure x_train is float32
x_train = x_train.astype(np.float32)
# Ensure y_train is float32
y_train = y_train.astype(np.float32)

# Print shapes
print(f"x_train shape: {x_train.shape}, dtype: {x_train.dtype}")
print(f"y_train shape: {y_train.shape}, dtype: {y_train.dtype}")
print("✅ Dataset successfully loaded!")


model.fit(x_train, y_train, epochs=20, batch_size=32, validation_split=0.1, shuffle=True)

# Save the trained model
model_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models", "sign_language_model.h5")
os.makedirs(os.path.dirname(model_save_path), exist_ok=True)  # Create models folder if not exist
model.save(model_save_path)

print(f" Model saved successfully at {model_save_path}")

