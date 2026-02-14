# from flask import Flask, render_template, request, jsonify, send_file
# import os
# import gtts
# import cv2
# from moviepy import VideoFileClip, concatenate_videoclips
# import numpy as np
# import mediapipe as mp
# # from moviepy.editor import * 

# app = Flask(__name__)

# # MediaPipe Hands model for gesture recognition
# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands()
# mp_draw = mp.solutions.drawing_utils

# @app.route("/text_to_sign", methods=["POST"])
# def text_to_sign():
#     data = request.get_json()
#     text = data.get("text")

#     if not text:
#         return jsonify({"error": "No text provided"}), 400

#     # Generate speech from text
#     tts = gtts.gTTS(text, lang="en")
#     tts.save("audio.mp3")

#     # Generate sign language video (Placeholder: Use real dataset in production)
#     sign_video_path = generate_sign_video(text)

#     # If video is not found, return an error response
#     if not sign_video_path:
#         return jsonify({"error": "Sign video not found"}), 404
    
#     return send_file(sign_video_path, as_attachment=True)

# def generate_sign_video(text):
#     # Placeholder function: Load pre-recorded sign language gestures for each word
#     video_clips = []
    
#     for word in text.split():
#         word_video_path = f"sign_videos/{word}.mp4"  # Ensure word videos exist in this folder
#         if os.path.exists(word_video_path):
#             video_clips.append(VideoFileClip(word_video_path))
    
#     if video_clips:
#         final_video = concatenate_videoclips(video_clips)
#         final_video_path = "generated_sign_language.mp4"
#         final_video.write_videofile(final_video_path, codec="libx264", fps=24)
#         return final_video_path
#     else:
#         return None

# if __name__ == "__main__":
#     app.run(debug=True)



from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import gtts
import cv2
from moviepy import VideoFileClip, concatenate_videoclips  # ✅ Fixed import
import numpy as np
import mediapipe as mp
from flask_cors import CORS  # ✅ Allow frontend to talk to Flask

app = Flask(__name__, 
            static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../static")),
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), "../templates"))
           )
CORS(app)  # ✅ Allows Cross-Origin Requests from frontend

# MediaPipe Hands model for gesture recognition
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils




@app.route("/text_to_sign", methods=["POST"]) 
def text_to_sign():
    print("✅ Route accessed successfully!")  # 🔍 Debugging
    try:
        data = request.get_json()
        print("Received Data:", data)

        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data["text"]
        print("Processing Text:", text)

        tts = gtts.gTTS(text, lang="en")
        tts.save("audio.mp3")

        sign_video_path = generate_sign_video(text)
        if not sign_video_path:
            return jsonify({"error": "No matching sign videos found"}), 404

        return send_file(sign_video_path, mimetype='video/mp4', as_attachment=True)

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500



def generate_sign_video(text):
    video_clips = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "sign_videos"))

    for word in text.split():
        word_video_path = os.path.join(base_dir, f"{word.lower()}.mp4")
        print(f"Checking for video: {word_video_path}")
        if os.path.exists(word_video_path):
            print(f"✅ Found: {word_video_path}")
            video_clips.append(VideoFileClip(word_video_path))
        else:
            print(f"❌ Not Found: {word_video_path}")
    
    if video_clips:
        final_video = concatenate_videoclips(video_clips)
        final_video_path = os.path.join(base_dir, "generated_sign_language.mp4")
        final_video.write_videofile(final_video_path, codec="libx264", fps=24)
        final_video.close()
        return final_video_path
    else:
        return None


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST"
    return response


