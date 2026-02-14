import speech_recognition as sr
from flask import Flask, request, jsonify

app = Flask(__name__)
recognizer = sr.Recognizer()

@app.route("/speech_to_text", methods=["POST"])
def speech_to_text():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return jsonify({"text": text})
    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"})
    except sr.RequestError:
        return jsonify({"error": "Speech recognition service unavailable"})

if __name__ == "__main__":
    app.run(debug=True)
