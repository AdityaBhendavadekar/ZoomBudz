# Zoom Audio Recorder and Transcriber

This project records Zoom call audio using **VB-Audio Virtual Cable**, transcribes the audio using **OpenAI Whisper**, and saves the transcription to text files.

---

## 🔧 Prerequisites

- A Windows system
- Python 3.10 or later installed ([Download Python](https://www.python.org/))
- Zoom installed
- Speakers or headphones connected

---

## 📥 Installation

### 1. Download VB-Audio Virtual Cable

- Official website: [https://vb-audio.com/Cable/](https://vb-audio.com/Cable/)
- Direct download link:  
  [Download VBCABLE_Driver_Pack45.zip](https://download.vb-audio.com/Download_CABLE/VBCABLE_Driver_Pack45.zip)

### 2. Install the Driver

- Extract the ZIP file.
- Run `VBCABLE_Setup.exe` (or `VBCABLE_Setup64.exe` for 64-bit systems) as Administrator.
- Click **Install Driver**.
- Restart your computer if prompted.

---

## 🎧 Setup Zoom with VB-Audio Virtual Cable

### 1. Set Zoom's Speaker Output to Virtual Cable

- Open Zoom.
- Go to `Settings > Audio > Speaker`.
- Select **VB-Audio Virtual Cable** as the output device.

### 2. Enable Monitoring for the Virtual Cable

This step allows you to hear the Zoom audio while it’s routed through the virtual cable.

- Right-click the **speaker icon** in the taskbar and select **Sounds**.
- Go to the **Recording** tab.
- Select **VB-Audio Virtual Cable** and click **Properties**.
- Switch to the **Listen** tab.
- Check **Listen to this device**.
- Under **Playback through this device**, choose your actual output device (e.g., speakers or headphones).
- Click **Apply** and **OK**.

---

## 🐍 Python Environment Setup

### 1. Create a Virtual Environment

1. Open a terminal or command prompt.
2. Navigate to the project directory:
   ```bash
   cd path/to/project
   ```
3. Create a virtual environment:
   ```bash
   python -m venv env
   ```
4. Activate the virtual environment:
   - **Windows**:
     ```bash
     env\Scripts\activate
     ```
   - **Mac/Linux**:
     ```bash
     source env/bin/activate
     ```

### 2. Install Required Libraries

1. Ensure the virtual environment is activated.
2. Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Install FFmpeg

Whisper requires FFmpeg for audio processing. Follow these steps to install and set it up:

1. Download FFmpeg:
   - Official website: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Direct link for Windows builds: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

2. Extract the ZIP file to a folder (e.g., ffmpeg).

3. Add FFmpeg to the system PATH:
   - Open **System Properties** > **Advanced** > **Environment Variables**.
   - Under **System Variables**, find `Path` and click **Edit**.
   - Add the `bin` folder of FFmpeg (e.g., bin).
   - Click **OK** to save.

4. Verify the installation:
   ```bash
   ffmpeg -version
   ```
   If installed correctly, this will display the FFmpeg version.

---

## 🚀 Running the Application

1. Ensure the virtual environment is activated:
   ```bash
   env\Scripts\activate
   ```
2. Run the Python script:
   ```bash
   python audio.py
   ```

---

## 📋 Summary of Commands

### Virtual Environment Setup
```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
```

### FFmpeg Installation
1. Download and extract FFmpeg.
2. Add the `bin` folder to the system PATH.
3. Verify installation:
   ```bash
   ffmpeg -version
   ```

### Running the Script
```bash
python audio.py
```

---

## 📂 Output

- **Audio Files**: Saved in the `audio_chunks` directory as `chunk_1.wav`, `chunk_2.wav`, etc.
- **Transcription Files**: Saved in the `audio_chunks` directory as `chunk_1.txt`, `chunk_2.txt`, etc.

---