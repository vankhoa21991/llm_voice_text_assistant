import streamlit as st
from whisper_cpp import Whisper
from ffmpeg import FFmpeg
import os
import datetime
import time
import wave
import numpy as np
import base64
import pyaudio
import asyncio

from dotenv import load_dotenv
load_dotenv()
import requests
import os

API_URL = os.getenv("API_URL")

@st.cache_resource
def ffmpegconvert(x):
    ffmpeg = FFmpeg().input(x).output("temp.wav", {"codec:a": "pcm_s16le",
                                                            'ar':16000,
                                                            'ac':1})
    ffmpeg.execute()
    pass

if "gentime" not in st.session_state:
    st.session_state.gentime = "**:green[none yet]**"
if "audiofile" not in st.session_state:
    st.session_state.audiofile = ''    

def diary():
    # st.set_page_config(layout="wide", page_title="AI Whisper Transcriber")
    st.write("# 🎙️✍️ Talk to your AI assistance!!\n\n\n")
    st.markdown('\n---\n', unsafe_allow_html=True)
    st.sidebar.write("## Upload an audio file or record :gear:")

    file1 = None
    transcribe_btn = st.button('✨ **Start AI Magic**', type='primary')

    st.markdown("\n\n")
    message1 = st.empty()
    message11 = st.empty()
    message2 = st.empty()
    message3 = st.empty()
    audioplayer = st.empty()
    transcribed = st.empty()

    # Upload the audio file
    file1 = st.sidebar.file_uploader("Upload Audio file", type=["mp3", "wav"], accept_multiple_files=False)
    gentimetext = st.sidebar.empty()

    model_list = requests.get(f"{API_URL}/get-voice-model-list")

    if model_list.status_code == 200:
        model_data = model_list.json().get("models", [])
        if isinstance(model_data, dict):
            # If the response is a list of models, just use it directly
            model_lists = model_data
        else:
            print("Unexpected response format. Expected a list.")
    else:
        print(f"Failed to retrieve model list: {model_list.status_code}")

    # Dropdown for model selection
    selected_model = st.sidebar.selectbox("Select Model:", model_lists)

    # Session state
    if 'text' not in st.session_state:
        st.session_state['text'] = 'Listening...'
        st.session_state['run'] = False
        st.session_state['frames'] = []

    # Audio parameters 
    st.sidebar.header('Audio Parameters')

    FRAMES_PER_BUFFER = 3200 #int(st.sidebar.text_input('Frames per buffer', 3200))
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000 #int(st.sidebar.text_input('Rate', 16000))
    p = pyaudio.PyAudio()

    # Open an audio stream with above parameter settings
    stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
    )

    # Capture audio
    async def record_audio():
        while st.session_state['run']:
            data = stream.read(FRAMES_PER_BUFFER)
            st.session_state['frames'].append(data)
            await asyncio.sleep(0.01)  # Allow asyncio to run other tasks

    # Asynchronous task to record audio
    if st.session_state['run']:
        asyncio.run(record_audio())

    # Start/stop audio transmission
    def start_listening():
        st.session_state['run'] = True
        st.session_state['frames'] = []  # Reset frames when restarting

    def stop_listening():
        st.session_state['run'] = False
        save_audio_file()  # Save the audio file when stopped

    # Save the audio to a .wav file
    def save_audio_file(filename="output.wav"):
        """Function to save recorded audio as a .wav file"""
        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(st.session_state['frames']))
        wf.close()
        st.success(f"Audio file saved as {filename}!")

        # Provide download button
        with open(filename, "rb") as f:
            st.download_button(
                label="Download .wav file",
                data=f,
                file_name=filename,
                mime="audio/wav"
            )

    

    col1, col2 = st.columns(2)

    col1.button('Start', on_click=start_listening)
    col2.button('Stop', on_click=stop_listening)

    if transcribe_btn and file1:
        with st.spinner("Transcribing..."):
            # Upload the file to FastAPI for transcription
            files = {"file": file1.getvalue()}  # Convert file to bytes to send in request
            data = {"model_name": selected_model}

            try:
                response = requests.post(f"{API_URL}/transcribe/",
                                         files=files, data=data)
                result = response.json()
                
                if response.status_code == 200:
                    message2.success(' Audio transcribed by AI', icon='✅')
                    transcribed.write(result["transcribed_text"])
                    st.session_state.gentime = f"**:green[{result['processing_time']}]**"
                    gentimetext.write(st.session_state.gentime)
                else:
                    message3.warning(result.get("message", "Error during transcription"), icon='⚠️')
            except Exception as e:
                message3.error(f"An error occurred: {str(e)}", icon='❌')
    

    if not file1:
        message3.warning("  Upload an audio file", icon='⚠️')
    if file1:
        if 'mp3' in file1.name:
            audioplayer.audio(file1.name, format="audio/mpeg")
        else:
            audioplayer.audio(file1.name, format="audio/wav")



if __name__ == "__main__":
    diary()