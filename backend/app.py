import subprocess  # For running external Python files
from flask import Flask, Response, jsonify, render_template, request
from backend.sign_to_text import get_text, clear_text
from backend.sign_to_text import generate_frames
import cv2
import numpy as np
import base64
import mediapipe as mp  # Import MediaPipe for hand tracking

app = Flask(__name__, static_folder="../static", template_folder="../templates")  # Set template directory

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(min_detection_confidence=0.2, min_tracking_confidence=0.2)  # Initialize Hands object
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)


@app.route("/")
def dashboard():
    print("Serving dashboard.html")  # Debugging log
    return render_template("dashboard.html")

@app.route('/gesture_navigation')
def gesture_navigation():
    return render_template('gesture_navigation.html')

@app.route("/get_text")
def get_text_route():
    return get_text()

@app.route("/clear_text", methods=["POST"])
def clear_text_route():
    return clear_text()

@app.route("/sign_to_text")
def sign_to_text():
    print("Serving sign_to_text.html")  # Debugging log
    return render_template("sign_to_text.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/text_to_sign", methods=["GET", "POST"])  # Add GET method
def text_to_sign():
    if request.method == "POST":
        from backend.text_to_sign import text_to_sign
        return text_to_sign()
    return render_template("text_to_sign.html")  # Render HTML for GET request

@app.route('/register_word', methods=['POST'])
def register_word():
    data = request.get_json()
    word = data.get("word")

    if not word:
        return jsonify({"error": "No word/character provided"}), 400

    # Run capture_images.py with the word as an argument
    try:
        subprocess.run(["python", "backend/capture_images.py", word], check=True)
        return jsonify({"message": f"Successfully registered '{word}'!"})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Error during execution: {e}"}), 500

@app.route("/process_gesture", methods=["POST"])
def process_gesture_live():
    try:
        data = request.get_json()
        image_data = data["image"].split(",")[1]
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        result = hands.process(img_rgb)
        if not result.multi_hand_landmarks:
            return jsonify({"gesture": "none"})

        landmarks = result.multi_hand_landmarks[0].landmark

        def is_finger_extended(start, mid, end):
            return landmarks[start].y > landmarks[mid].y > landmarks[end].y

        finger_states = {
            "thumb": landmarks[4].x > landmarks[3].x,
            "index": is_finger_extended(5, 6, 8),
            "middle": is_finger_extended(9, 10, 12),
            "ring": is_finger_extended(13, 14, 16),
            "pinky": is_finger_extended(17, 18, 20)
        }

        # Back Gesture: Thumb extended down, other fingers folded
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_base = landmarks[2]

        # Check if thumb is pointing down
        thumb_down = (
            thumb_tip.y > thumb_ip.y > thumb_base.y and  # Downward direction
            abs(thumb_tip.x - thumb_base.x) < 0.1 and    # Mostly vertical
            not any(finger_states[f] for f in ["index", "middle", "ring", "pinky"])  # Other fingers folded
        )

        if thumb_down:
            gesture = "go_back"

        elif all(finger_states.values()):
            gesture = "open_palm"
        elif finger_states["index"] and not any([finger_states["middle"], finger_states["ring"], finger_states["pinky"]]):
            index_tip = landmarks[8]
            index_base = landmarks[5]
            dx = index_tip.x - index_base.x
            dy = index_tip.y - index_base.y
            gesture = "point_up" if abs(dy) > abs(dx) else "point_right"
        elif not any(finger_states.values()):
            gesture = "closed_fist"
        else:
            gesture = "none"

        return jsonify({"gesture": gesture})

    except Exception as e:
        return jsonify({"error": str(e), "gesture": "error"})


if __name__ == "__main__":
    app.run(debug=True)
