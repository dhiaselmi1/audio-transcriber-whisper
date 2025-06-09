import streamlit as st
import requests
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Audio Transcriber",
    page_icon="🎤",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .upload-section {
        border: 2px dashed #1f77b4;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .transcription-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🎤 Audio Transcriber (OpenAI Whisper)</h1>', unsafe_allow_html=True)
st.markdown("Upload an audio file and get its transcription using OpenAI Whisper AI")

# Sidebar with information
st.sidebar.header("ℹ️ Information")
st.sidebar.markdown("""
**Supported Formats:**
- MP3 (.mp3)
- WAV (.wav) 
- M4A (.m4a)
- FLAC (.flac)
- OGG (.ogg)
- WebM (.webm)

**File Limits:**
- Maximum size: 25MB
- Maximum duration: ~30 minutes

**Instructions:**
1. Upload your audio file
2. Click 'Transcribe Audio'
3. Wait for processing
4. Download the result
""")

# Check backend health
st.sidebar.header("🔧 System Status")
try:
    health_response = requests.get("http://localhost:8000/health", timeout=5)
    if health_response.status_code == 200:
        health_data = health_response.json()
        if health_data.get("status") == "healthy":
            st.sidebar.success("✅ Backend is running")
        else:
            st.sidebar.error("❌ Backend has issues")
    else:
        st.sidebar.error("❌ Backend not responding")
except:
    st.sidebar.error("❌ Cannot connect to backend")
    st.sidebar.info("Make sure to run: `uvicorn backend.main:app --reload`")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # File uploader
    st.subheader("📁 Upload Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=["mp3", "wav", "m4a", "flac", "ogg", "webm"],
        help="Select an audio file to transcribe. Maximum size: 25MB"
    )

    if uploaded_file is not None:
        # Display file information
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)

        st.success(f"✅ File uploaded successfully!")

        # File details in an expander
        with st.expander("📋 File Details", expanded=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("File Name", uploaded_file.name)
            with col_b:
                st.metric("File Size", f"{file_size_mb:.2f} MB")
            with col_c:
                st.metric("File Type", uploaded_file.type)

        # Audio player
        st.subheader("🎵 Audio Preview")
        st.audio(uploaded_file, format='audio/wav')

        # Transcription section
        st.subheader("🎯 Transcription")

        # Transcribe button
        if st.button("🚀 Transcribe Audio", type="primary", use_container_width=True):
            if file_size_mb > 25:
                st.error("❌ File too large! Please upload a file smaller than 25MB.")
            else:
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    # Update progress
                    progress_bar.progress(25)
                    status_text.text("📤 Uploading file...")

                    # Prepare file for upload
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                    }

                    progress_bar.progress(50)
                    status_text.text("🔄 Processing audio...")

                    # Record start time
                    start_time = time.time()

                    # Send request to FastAPI backend
                    response = requests.post(
                        "http://localhost:8000/transcribe/",
                        files=files,
                        timeout=300  # 5 minute timeout for large files
                    )

                    progress_bar.progress(75)
                    status_text.text("📝 Generating transcription...")

                    if response.status_code == 200:
                        # Process successful response
                        result = response.json()
                        transcription = result.get("transcription", "No transcription available.")
                        language = result.get("language", "unknown")
                        processing_time = time.time() - start_time

                        progress_bar.progress(100)
                        status_text.text("✅ Transcription completed!")

                        # Display results
                        st.success(f"🎉 Transcription completed in {processing_time:.1f} seconds!")

                        # Transcription results
                        st.subheader("📄 Results")

                        # Language and stats
                        col_x, col_y, col_z = st.columns(3)
                        with col_x:
                            st.metric("Detected Language", language.upper())
                        with col_y:
                            st.metric("Character Count", len(transcription))
                        with col_z:
                            st.metric("Word Count", len(transcription.split()))

                        # Transcription text
                        st.text_area(
                            "Transcription Text:",
                            value=transcription,
                            height=200,
                            help="You can copy this text or download it as a file"
                        )

                        # Download options
                        col_download1, col_download2 = st.columns(2)

                        with col_download1:
                            # Download as TXT
                            st.download_button(
                                label="📥 Download as TXT",
                                data=transcription,
                                file_name=f"{uploaded_file.name}_transcription.txt",
                                mime="text/plain",
                                use_container_width=True
                            )

                        with col_download2:
                            # Download with metadata
                            metadata = f"""Audio Transcription Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
File: {uploaded_file.name}
Size: {file_size_mb:.2f} MB
Language: {language}
Processing Time: {processing_time:.1f} seconds

--- TRANSCRIPTION ---
{transcription}
"""
                            st.download_button(
                                label="📊 Download Report",
                                data=metadata,
                                file_name=f"{uploaded_file.name}_report.txt",
                                mime="text/plain",
                                use_container_width=True
                            )

                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()

                    else:
                        progress_bar.empty()
                        status_text.empty()
                        st.error(f"❌ Error {response.status_code}: {response.text}")

                except requests.exceptions.Timeout:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("⏰ Request timed out. Please try with a shorter audio file.")

                except requests.exceptions.ConnectionError:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("🔌 Cannot connect to the backend server. Make sure it's running on http://localhost:8000")
                    st.info("Run this command in your terminal: `uvicorn backend.main:app --reload`")

                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ An unexpected error occurred: {str(e)}")

with col2:
    # Tips and information
    st.subheader("💡 Tips")
    st.info("""
    **For best results:**
    - Use clear audio recordings
    - Minimize background noise
    - Ensure good audio quality
    - Keep files under 25MB
    """)

    st.subheader("⚡ Performance")
    st.warning("""
    **Processing Time:**
    - Small files (<5MB): ~10-30 seconds
    - Medium files (5-15MB): ~30-90 seconds  
    - Large files (15-25MB): ~2-5 minutes
    """)

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ using [OpenAI Whisper](https://openai.com/research/whisper), "
    "[FastAPI](https://fastapi.tiangolo.com/), and [Streamlit](https://streamlit.io/)"
)