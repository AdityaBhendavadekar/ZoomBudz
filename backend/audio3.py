import whisper
import pyaudio
import numpy as np
import tempfile
import wave

# Audio recording parameters
RATE = 44100  # Sample rate (matches Zoom's output)
CHUNK = 1024  # Buffer size

def list_input_devices():
    """List all available audio input devices."""
    p = pyaudio.PyAudio()
    print("Available audio input devices:\n")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"{i}: {info['name']}")
    p.terminate()

def save_audio_to_wav(audio_data, rate):
    """Save audio data to a temporary WAV file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        with wave.open(temp_wav.name, 'wb') as wf:
            wf.setnchannels(1)  # Mono audio
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(rate)
            wf.writeframes(audio_data)
        return temp_wav.name

def transcribe_zoom_audio(device_index=None):
    """Capture audio from Zoom and transcribe it in real-time using Whisper."""
    if device_index is None:
        print("Error: Please provide a valid input device index.")
        list_input_devices()
        return

    # Load the Whisper model
    model = whisper.load_model("base")  # Use "tiny", "base", "small", "medium", or "large"

    # Initialize PyAudio for capturing audio
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,  # 16-bit audio format
        channels=2,             # Stereo audio
        rate=RATE,              # Sampling rate
        input=True,             # Enable input stream
        input_device_index=device_index,
        frames_per_buffer=CHUNK
    )

    print(f"Listening for audio from device index {device_index}... Press Ctrl+C to stop.")

    try:
        while True:
            # Read audio data
            audio_data = stream.read(CHUNK)

            # Save audio to a temporary WAV file
            wav_path = save_audio_to_wav(audio_data, RATE)

            # Transcribe audio using Whisper
            result = model.transcribe(wav_path, fp16=False)
            print(f"Transcript: {result['text']}")
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # Clean up resources
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    # Uncomment this line to list audio devices
    # list_input_devices()

    # Replace this with the correct device index after listing devices
    transcribe_zoom_audio(device_index=2)