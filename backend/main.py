from fastapi import FastAPI, UploadFile, File, HTTPException
import whisper
import os
import uuid
import subprocess
from pathlib import Path
from typing import Dict
import traceback

app = FastAPI(title="Audio Transcription API", version="1.0.0")

# Global model and temp directory
model = whisper.load_model("base")
TEMP_DIR = os.path.join(os.getcwd(), "temp_audio")
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Audio Transcription API is running."}



@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/transcribe/")
async def transcribe_audio(file: UploadFile = File(...)) -> Dict[str, str]:
    # Basic validation
    if model is None:
        raise HTTPException(status_code=500, detail="Whisper model not loaded")

    # Read file
    audio_bytes = await file.read()
    file_size = len(audio_bytes)
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    if file_size > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (>25MB)")

    # Validate extension
    file_ext = Path(file.filename).suffix.lower()
    allowed_exts = [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"]
    if file_ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{file_ext}'")

    # Save temp file
    unique_id = str(uuid.uuid4())[:8]
    temp_file_path = os.path.join(TEMP_DIR, f"audio_{unique_id}{file_ext}")
    try:
        with open(temp_file_path, 'wb') as f:
            f.write(audio_bytes)

        # Optional: Validate with ffmpeg
        subprocess.run(['ffmpeg', '-i', temp_file_path, '-f', 'null', '-'],
                       capture_output=True, text=True, timeout=30)

        # Transcribe
        result = model.transcribe(temp_file_path, fp16=False, verbose=False)
        transcription = result["text"].strip()
        language = result.get("language", "unknown")

        return {
            "transcription": transcription,
            "filename": file.filename,
            "file_size": str(file_size),
            "language": language
        }

    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

    finally:
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
