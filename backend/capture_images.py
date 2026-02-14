import subprocess
import cv2
import os
import sys  # To accept command-line arguments

# Define the gesture label (change this before running)
# SIGN_LABEL = "no"  # Example: Change this to "Yes", "No", etc.

# Check for argument from app.py
if len(sys.argv) < 2:
    print("❌ Error: No word/char provided.")
    sys.exit(1)

SIGN_LABEL = sys.argv[1]  # Word from frontend input

# Define path to save images
SAVE_PATH = f"datasets/sign_images/{SIGN_LABEL}/"
os.makedirs(SAVE_PATH, exist_ok=True)  # Create folder if it doesn't exist

# Initialize webcam
cap = cv2.VideoCapture(0)
count = 0  # Image counter

print(f"📸 Capturing images for label: {SIGN_LABEL}. Press 'Q' to stop.")

while count < 100:  # Capture 100 images
    success, frame = cap.read()
    if not success:
        print("⚠️ ERROR: Cannot read frame from webcam!")
        break

    # Show frame
    cv2.imshow("Capture Gesture", frame)

    # Save image
    img_path = f"{SAVE_PATH}/img{count}.jpg"
    cv2.imwrite(img_path, frame)
    print(f"✅ Saved: {img_path}")

    count += 1

    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("📌 Image capture complete! 🎉")


# Trigger extract_landmarks.py automatically
try:
    subprocess.run(["python", "backend/extract_landmarks.py"], check=True)
    print("✅ Landmarks successfully extracted and saved!")
except subprocess.CalledProcessError as e:
    print(f"❌ Error during landmarks extraction: {e}")
