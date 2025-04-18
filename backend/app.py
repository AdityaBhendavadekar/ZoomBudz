from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
import os
import pyaudio
import wave
import whisper

app = Flask(__name__)
CORS(app)

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

def list_input_devices():
    """List all available audio input devices."""
    p = pyaudio.PyAudio()
    print("Available audio input devices:\n")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"{i}: {info['name']}")
    p.terminate()

def record_audio():
    """Record audio in chunks."""
    global is_recording, chunk_number
    device_index = 2  # Replace with the correct device index for VB-Audio Virtual Cable
    os.makedirs("audio_chunks", exist_ok=True)

    while is_recording:
        chunk_filename = f"audio_chunks/chunk_{chunk_number}.wav"
        record_audio_chunk(chunk_filename, device_index, CHUNK_DURATION)
        transcribe_audio(chunk_filename, chunk_number)  # Transcribe after recording
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

def transcribe_audio(file_path, chunk_number):
    """Transcribe audio using Whisper and save the transcription to a text file."""
    print(f"Transcribing {file_path}...")
    model = whisper.load_model("base")  # Use "tiny", "base", "small", "medium", or "large"
    result = model.transcribe(file_path)
    transcription = result['text']
    print(f"Transcription for chunk {chunk_number}:\n{transcription}")

    # Save transcription to a text file
    text_filename = f"audio_chunks/chunk_{chunk_number}.txt"
    with open(text_filename, 'w', encoding='utf-8') as text_file:
        text_file.write(transcription)
    print(f"Saved transcription to {text_filename}")

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

if __name__ == "__main__":
    app.run(port=5000)