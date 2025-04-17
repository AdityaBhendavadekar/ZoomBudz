import pyaudio
import wave

def list_input_devices():
    p = pyaudio.PyAudio()
    print("Available audio input devices:\n")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"{i}: {info['name']}")
    p.terminate()

def record_zoom_audio(output_filename="zoom_call.wav", device_index=None, record_seconds=60):
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024

    p = pyaudio.PyAudio()

    if device_index is None:
        print("Error: Please provide a valid input device index.")
        list_input_devices()
        return

    print(f"Recording from device index {device_index}...")

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK)

    frames = []

    try:
        for _ in range(0, int(RATE / CHUNK * record_seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        print("\nRecording interrupted by user.")

    print("Recording complete.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Saved to {output_filename}")

if __name__ == "__main__":
    # Uncomment this line to list audio devices
    # list_input_devices()

    # Replace this with the correct device index after listing devices
    record_zoom_audio(device_index=2, record_seconds=120)
