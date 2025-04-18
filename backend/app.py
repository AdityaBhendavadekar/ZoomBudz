from flask import Flask, jsonify, request
from threading import Thread
import os
import pyaudio
import wave
import whisper

app = Flask(__name__)

# Global variables
is_recording = False
chunk_number = 1
recording_thread = None

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
CHUNK_DURATION = 2 * 60  # 2 minutes in seconds for testing

def record_audio():
    """Record audio in chunks."""
    global is_recording, chunk_number
    device_index = 2  # Replace with the correct device index for VB-Audio Virtual Cable
    os.makedirs("audio_chunks", exist_ok=True)

    while is_recording:
        chunk_filename = f"audio_chunks/chunk_{chunk_number}.wav"
        record_audio_chunk(chunk_filename, device_index, CHUNK_DURATION)
        chunk_number += 1

def record_audio_chunk(output_filename, device_index, record_seconds):
    """Record a chunk of audio and save it to a file."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK)

    frames = []
    print(f"Recording chunk: {output_filename}...")
    try:
        for _ in range(0, int(RATE / CHUNK * record_seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        print("\nRecording interrupted by user.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Saved chunk to {output_filename}")

@app.route('/start', methods=['POST'])
def start_recording():
    """Start recording audio."""
    global is_recording, recording_thread
    if not is_recording:
        is_recording = True
        recording_thread = Thread(target=record_audio)
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

@app.route('/transcribe', methods=['GET'])
def get_transcriptions():
    """Get transcriptions of all recorded chunks."""
    transcriptions = {}
    model = whisper.load_model("base")
    for filename in os.listdir("audio_chunks"):
        if filename.endswith(".wav"):
            filepath = os.path.join("audio_chunks", filename)
            result = model.transcribe(filepath)
            transcriptions[filename] = result['text']
    return jsonify(transcriptions)

if __name__ == "__main__":
    app.run(port=5000)