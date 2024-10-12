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


@st.cache_resource 
def create_whisper():   
    whisper = Whisper("models/ggml-tiny.en-q8_0.bin")
    return whisper

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
    whisper = create_whisper()
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
            print(file1.name)
            if 'mp3' in file1.name:
                print('The file is an MP3: starting ffmpeg')
                message1.info(' Your Audio file is a MP3: we are going to convert it!', icon='⏳')
                out = ffmpegconvert(file1.name)
                message11.success(' Audio file correctly encoded into WAV 16k Mono', icon='✅')
                start = datetime.datetime.now()
                print('Start transcribing...')
                whisper.transcribe('temp.wav', 
                                diarize=False,
                                print_progress=False) 
                delta = datetime.datetime.now() - start
                st.session_state.gentime = f"**:green[{str(delta)}]**"
                gentimetext.write(st.session_state.gentime)
                message2.success(' Audio transcribed by AI', icon='✅')
                print('removing temp files...')
                try:
                    os.remove('temp.wav')
                except:
                    pass    
                print('writing text file out...')
                result = whisper.output('AITranscribed', output_txt=True, output_srt=True)
                st.toast('Output files **AITranscribed** saved!', icon='🎉')
                time.sleep(1.2)
                st.toast('**text** file saved', icon='📃')
                time.sleep(1.2)
                st.toast('**subtitles** file saved', icon='🪩')
                transcribed.write(result)
                print('completed')

            else:             
                start = datetime.datetime.now()
                whisper.transcribe(file1.name, 
                                diarize=False,
                                print_progress=False)
                delta = datetime.datetime.now() - start
                st.session_state.gentime = f"**:green[{str(delta)}]**" 
                gentimetext.write(st.session_state.gentime)
                message2.success(' Audio transcribed by AI', icon='✅')                
                result = whisper.output('AITranscribed', output_txt=True, output_srt=True)
                st.toast('Output files **AITranscribed** saved!', icon='🎉')
                time.sleep(1.2)
                st.toast('**text** file saved', icon='📃')
                time.sleep(1.2)
                st.toast('**subtitles** file saved', icon='🪩')
                transcribed.write(result)
    

    if not file1:
        message3.warning("  Upload an audio file", icon='⚠️')
    if file1:
        if 'mp3' in file1.name:
            audioplayer.audio(file1.name, format="audio/mpeg")
        else:
            audioplayer.audio(file1.name, format="audio/wav")



if __name__ == "__main__":
    diary()