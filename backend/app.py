from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
import audio_handler

app = Flask(__name__)
CORS(app)

# Global variables
is_recording = False
chunk_number = 1
recording_thread = None

def record_audio_wrapper():
    """Wrapper function to handle global variables for the audio handler."""
    global is_recording, chunk_number
    # Use lists to pass by reference since integers are immutable
    is_recording_ref = [is_recording]
    chunk_number_ref = [chunk_number]
    
    audio_handler.record_audio(is_recording_ref, chunk_number_ref)
    
    # Update global variables after recording
    chunk_number = chunk_number_ref[0]

@app.route('/start', methods=['POST'])
def start_recording():
    """Start recording audio."""
    global is_recording, recording_thread
    if not is_recording:
        is_recording = True
        recording_thread = Thread(target=record_audio_wrapper)
        recording_thread.start()
        return jsonify({"status": "Recording started"})
    return jsonify({"status": "Already recording"})

@app.route('/stop', methods=['POST'])
def stop_recording():
    """Stop recording audio."""
    global is_recording, recording_thread
    if is_recording:
        is_recording = False
        recording_thread.join()
        return jsonify({"status": "Recording stopped"})
    return jsonify({"status": "Not recording"})

if __name__ == "__main__":
    app.run(port=5000)