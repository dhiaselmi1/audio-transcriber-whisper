# 🎤 Audio Transcriber (OpenAI Whisper + FastAPI + Streamlit)

A full-stack web application that transcribes audio files into text using OpenAI's Whisper ASR model. Built with a **FastAPI backend** and a **Streamlit frontend**, this app supports multiple audio formats, displays transcription stats, and allows users to download the output.

---

## 🚀 Features

- 🎵 Upload audio files (MP3, WAV, M4A, FLAC, OGG, WebM)
- 🌍 Detect spoken language automatically
- 📝 Get full transcriptions of spoken content
- 📥 Download transcriptions and detailed reports
- 📊 View word count, character count, processing time
- ✅ Real-time health check for backend

---


## 🧰 Tech Stack

| Layer      | Technology        |
|------------|-------------------|
| Frontend   | Streamlit         |
| Backend    | FastAPI           |
| ASR Model  | OpenAI Whisper    |
| Utilities  | FFmpeg            |
| Language   | Python            |


---

## 🚀 How to Run the Project

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/audio-transcriber.git
cd acme-review-analyzer
```
2.  **Create and activate a Python virtual environment**:
    ```bash
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    # Or Windows (CMD):
    .\venv\Scripts/activate.bat
    ```
3.  **Install dependencies**:
    ```bash
    pip install streamlit fastapi uvicorn requests openai-whisper
    ```
4.  **Install FFmpeg**:
    ```bash
    choco install ffmpeg
    ```
  ## ▶️ Running the Application

1.  **Start the FastAPI backend server**:
    ```bash
    uvicorn backend.main:app --reload
    ```

2.  **In a new terminal, start the Streamlit frontend**:
    ```bash
    streamlit run frontend/app.py
    ```
    Open your browser to `http://localhost:8501`.

---
