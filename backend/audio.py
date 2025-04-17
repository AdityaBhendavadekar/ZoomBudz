import pyaudio
import wave
import whisper
import os
from threading import Thread

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

    return transcription

def process_chunk(chunk_filename, chunk_number):
    """Process a recorded chunk: transcribe and save the text."""
    transcribe_audio(chunk_filename, chunk_number)

def main():
    # List input devices and set the correct device index
    # Uncomment the next line to list devices
    # list_input_devices()
    device_index = 2  # Replace with the correct device index for VB-Audio Virtual Cable

    # Create a directory to store audio chunks
    os.makedirs("audio_chunks", exist_ok=True)

    chunk_number = 1
    previous_thread = None

    while True:
        chunk_filename = f"audio_chunks/chunk_{chunk_number}.wav"

        # Record a chunk
        record_audio_chunk(chunk_filename, device_index, CHUNK_DURATION)

        # Start transcription of the previous chunk in a separate thread
        if previous_thread is not None:
            previous_thread.join()  # Ensure the previous transcription is complete

        previous_thread = Thread(target=process_chunk, args=(chunk_filename, chunk_number))
        previous_thread.start()

        # Move to the next chunk
        chunk_number += 1

if __name__ == "__main__":
    main()