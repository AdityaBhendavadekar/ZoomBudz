import pyaudio
import numpy as np
import wave
import threading
import time
import os
import speech_recognition as sr
from datetime import datetime
import queue
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.io import wavfile
import librosa
import librosa.display

class ZoomAudioAnalyzer:
    def __init__(self, format=pyaudio.paInt16, channels=1, rate=16000, chunk=1024, 
                 record_seconds=120, output_dir="recordings"):
        """
        Initialize the Zoom audio analyzer.
        
        Args:
            format: Audio format (default: pyaudio.paInt16)
            channels: Number of audio channels (default: 1 for mono)
            rate: Sampling rate (default: 16000 Hz)
            chunk: Audio chunk size (default: 1024)
            record_seconds: Maximum recording duration in seconds (default: 120)
            output_dir: Directory to save audio recordings (default: "recordings")
        """
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.record_seconds = record_seconds
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        
        # Analysis results
        self.is_speech_active = False
        self.current_volume = 0
        self.speech_text = ""
        self.is_recording = False
        self.audio_data_queue = queue.Queue()
        
        # Audio frames and analysis data
        self.frames = []
        self.volume_history = []
        self.speech_activity_history = []

    def _get_input_device_index(self):
        """
        Find the default input device index or suitable device for audio capture.
        """
        info = self.p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        # Try to find a device with "Zoom" in its name
        for i in range(num_devices):
            device_info = self.p.get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                name = device_info.get('name')
                if 'zoom' in name.lower():
                    print(f"Found Zoom audio device: {name}")
                    return i
        
        # If no Zoom device found, return default input device
        default_device = self.p.get_default_input_device_info()
        print(f"Using default input device: {default_device.get('name')}")
        return default_device.get('index')

    def start_recording(self):
        """
        Start recording and analyzing audio.
        """
        if self.is_recording:
            print("Already recording!")
            return
            
        self.is_recording = True
        self.frames = []
        self.volume_history = []
        self.speech_activity_history = []
        
        # Start recording thread
        record_thread = threading.Thread(target=self._record_audio)
        record_thread.daemon = True
        record_thread.start()
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=self._analyze_audio)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        print("Recording and analysis started!")

    def stop_recording(self):
        """
        Stop recording and save the audio file.
        """
        if not self.is_recording:
            print("Not recording!")
            return
            
        self.is_recording = False
        time.sleep(0.5)  # Wait for threads to finish
        
        # Save recording
        if len(self.frames) > 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, f"zoom_recording_{timestamp}.wav")
            
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            
            print(f"Recording saved to {filename}")
            
            # Perform full analysis on saved file
            self._analyze_saved_file(filename)
        else:
            print("No audio data captured!")

    def _record_audio(self):
        """
        Record audio from the input device.
        """
        try:
            # Try to find an appropriate input device
            device_index = self._get_input_device_index()
            
            stream = self.p.open(format=self.format,
                                channels=self.channels,
                                rate=self.rate,
                                input=True,
                                input_device_index=device_index,
                                frames_per_buffer=self.chunk)
            
            print("Recording started...")
            
            # Record until stopped or maximum duration reached
            max_chunks = int(self.rate / self.chunk * self.record_seconds)
            
            for _ in range(max_chunks):
                if not self.is_recording:
                    break
                    
                data = stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
                
                # Add to queue for real-time analysis
                self.audio_data_queue.put(data)
                
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Error during recording: {e}")
            self.is_recording = False

    def _analyze_audio(self):
        """
        Analyze audio data in real-time.
        """
        accumulated_frames = []
        last_transcription_time = time.time()
        
        while self.is_recording:
            try:
                # Get audio chunk from queue
                if not self.audio_data_queue.empty():
                    data = self.audio_data_queue.get()
                    
                    # Analyze volume
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    self.current_volume = np.abs(audio_data).mean()
                    self.volume_history.append(self.current_volume)
                    
                    # Check if there's speech (simple threshold-based detection)
                    speech_threshold = 1000  # Adjust based on your microphone
                    self.is_speech_active = self.current_volume > speech_threshold
                    self.speech_activity_history.append(1 if self.is_speech_active else 0)
                    
                    # Print info every second
                    if len(self.volume_history) % 16 == 0:
                        print(f"Current volume: {self.current_volume:.2f}, "
                              f"Speech active: {self.is_speech_active}")
                    
                    # Accumulate frames for speech recognition
                    accumulated_frames.append(data)
                    
                    # Perform speech recognition every 3 seconds
                    current_time = time.time()
                    if current_time - last_transcription_time > 3 and self.is_speech_active:
                        # Create a WAV file in memory from accumulated frames
                        recognizer_thread = threading.Thread(
                            target=self._recognize_speech,
                            args=(accumulated_frames.copy(),)
                        )
                        recognizer_thread.daemon = True
                        recognizer_thread.start()
                        
                        # Reset for next analysis
                        accumulated_frames = []
                        last_transcription_time = current_time
                
                time.sleep(0.01)  # Small delay to prevent CPU overuse
                
            except Exception as e:
                print(f"Error during analysis: {e}")
                time.sleep(0.1)

    def _recognize_speech(self, frames):
        """
        Perform speech recognition on accumulated frames.
        
        Args:
            frames: List of audio frames
        """
        try:
            # Create a WAV file in memory
            audio_data = b''.join(frames)
            
            # Create a temporary WAV file
            temp_filename = os.path.join(self.output_dir, "temp_recognition.wav")
            
            wf = wave.open(temp_filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(audio_data)
            wf.close()
            
            # Use speech recognition
            with sr.AudioFile(temp_filename) as source:
                audio = self.recognizer.record(source)
                
                try:
                    text = self.recognizer.recognize_google(audio)
                    self.speech_text = text
                    print(f"Recognized: {text}")
                    
                    # Here you can perform topic detection or other analysis on the text
                    
                except sr.UnknownValueError:
                    pass  # Speech wasn't understandable
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
            
            # Clean up temp file
            os.remove(temp_filename)
            
        except Exception as e:
            print(f"Error in speech recognition: {e}")

    def _analyze_saved_file(self, filename):
        """
        Perform comprehensive analysis on a saved audio file.
        
        Args:
            filename: Path to the audio file
        """
        try:
            print(f"Analyzing {filename}...")
            
            # Load audio file
            y, sr = librosa.load(filename, sr=None)
            
            # Extract features
            # 1. Spectral Centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # 2. Zero Crossing Rate
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)[0]
            
            # 3. MFCC (Mel-Frequency Cepstral Coefficients)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # 4. Spectral Contrast
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            
            # Generate plots
            plt.figure(figsize=(15, 10))
            
            # Plot waveform
            plt.subplot(3, 1, 1)
            librosa.display.waveshow(y, sr=sr)
            plt.title('Waveform')
            
            # Plot spectrogram
            plt.subplot(3, 1, 2)
            D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
            librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
            plt.colorbar(format='%+2.0f dB')
            plt.title('Spectrogram')
            
            # Plot MFCCs
            plt.subplot(3, 1, 3)
            librosa.display.specshow(mfccs, sr=sr, x_axis='time')
            plt.colorbar()
            plt.title('MFCCs')
            
            # Save plot
            analysis_filename = filename.replace('.wav', '_analysis.png')
            plt.tight_layout()
            plt.savefig(analysis_filename)
            plt.close()
            
            print(f"Analysis saved to {analysis_filename}")
            
            # Perform full speech recognition on the file
            self._transcribe_full_file(filename)
            
        except Exception as e:
            print(f"Error during full analysis: {e}")

    def _transcribe_full_file(self, filename):
        """
        Transcribe the entire audio file.
        
        Args:
            filename: Path to the audio file
        """
        try:
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(filename) as source:
                audio_data = recognizer.record(source)
                
            text = recognizer.recognize_google(audio_data)
            
            # Save transcription
            transcript_filename = filename.replace('.wav', '_transcript.txt')
            with open(transcript_filename, 'w') as f:
                f.write(text)
                
            print(f"Transcript saved to {transcript_filename}")
            
            # Here you can add more advanced analysis, like:
            # - Topic modeling
            # - Sentiment analysis
            # - Speaker identification
            # - Keyword extraction
            
        except Exception as e:
            print(f"Error during transcription: {e}")

    def get_current_analysis(self):
        """
        Get the current analysis results.
        
        Returns:
            dict: Current analysis results
        """
        return {
            "is_speech_active": self.is_speech_active,
            "current_volume": float(self.current_volume),
            "speech_text": self.speech_text,
            "is_recording": self.is_recording
        }
    
    def cleanup(self):
        """
        Clean up resources.
        """
        self.is_recording = False
        self.p.terminate()
        print("Audio analyzer resources cleaned up.")

    def visualize_realtime(self):
        """
        Visualize audio analysis in real-time.
        """
        # Set up the figure and axis
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Initialize plots
        volume_line, = ax1.plot([], [], lw=2)
        speech_line, = ax2.plot([], [], lw=2, color='red')
        
        ax1.set_ylim(0, 5000)  # Adjust based on your volume range
        ax1.set_title('Volume Level')
        ax1.set_ylabel('Volume')
        
        ax2.set_ylim(-0.1, 1.1)
        ax2.set_title('Speech Activity')
        ax2.set_ylabel('Active (1) / Inactive (0)')
        
        for ax in [ax1, ax2]:
            ax.set_xlim(0, 100)
            ax.set_xlabel('Time')
            ax.grid(True)
        
        def update_plot(frame):
            # Update volume history plot
            x = range(len(self.volume_history[-100:]) if len(self.volume_history) > 100 else len(self.volume_history))
            y = self.volume_history[-100:] if len(self.volume_history) > 100 else self.volume_history
            volume_line.set_data(x, y)
            
            # Update speech activity plot
            y_speech = self.speech_activity_history[-100:] if len(self.speech_activity_history) > 100 else self.speech_activity_history
            speech_line.set_data(x, y_speech)
            
            # Adjust axes if needed
            if len(x) > 0:
                ax1.set_xlim(0, len(x))
                ax2.set_xlim(0, len(x))
                
                # Update max volume for scaling
                if len(y) > 0:
                    max_vol = max(max(y), 1)
                    ax1.set_ylim(0, max_vol * 1.2)
            
            return volume_line, speech_line
        
        # Set up animation
        ani = FuncAnimation(fig, update_plot, frames=None, interval=100, blit=True)
        plt.tight_layout()
        plt.show()


def main():
    # Initialize the analyzer
    analyzer = ZoomAudioAnalyzer(output_dir="zoom_recordings")
    
    try:
        # Start recording and analyzing
        analyzer.start_recording()
        
        # Start visualization in a separate thread
        viz_thread = threading.Thread(target=analyzer.visualize_realtime)
        viz_thread.daemon = True
        viz_thread.start()
        
        # Run for a specific duration or until user interrupts
        print("Press Ctrl+C to stop recording...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Recording stopped by user")
    finally:
        # Stop recording and clean up
        analyzer.stop_recording()
        analyzer.cleanup()
        print("Analysis complete.")

if __name__ == "__main__":
    main()