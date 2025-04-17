import whisper
import pyaudio
import numpy as np

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
            # Read audio data from the virtual cable
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Transcribe audio using Whisper
            result = model.transcribe(audio_np, fp16=False)
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