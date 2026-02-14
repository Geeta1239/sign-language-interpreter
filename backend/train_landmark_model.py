import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

# ✅ Load processed landmarks
x_train = np.load("x_train.npy")
print("x_train shape:", x_train.shape)  # Should be (num_samples, 63)
y_train = np.load("y_train.npy")

print("x_train shape:", x_train.shape)  # Should be (num_samples, 63)
print("y_train shape:", y_train.shape)  # Should be (num_samples,)

# ✅ Normalize landmark values
x_train = x_train / np.max(x_train)

# ✅ Encode labels into numbers
from sklearn.preprocessing import LabelEncoder
encoder = LabelEncoder()
y_train = encoder.fit_transform(y_train)
print(encoder.classes_)

# ✅ One-hot encode labels
num_classes = len(encoder.classes_)
y_train = tf.keras.utils.to_categorical(y_train, num_classes)

# ✅ Build Model
model = Sequential([
    Dense(128, activation="relu", input_shape=(63,)),
    Dropout(0.3),
    Dense(64, activation="relu"),
    Dropout(0.2),
    Dense(num_classes, activation="softmax")
])

# ✅ Compile and Train
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
model.fit(x_train, y_train, epochs=20, batch_size=32, validation_split=0.1, shuffle=True)

# ✅ Save the Model
model.save("models/landmark_model.h5")
print("✅ Model training complete and saved as landmark_model.h5")
