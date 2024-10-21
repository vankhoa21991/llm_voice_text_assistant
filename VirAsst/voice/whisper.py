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
from typing import Optional
from VirAsst.modules import HF_MODELS_VOICE


# make a whisper handler
class ModelWhisperCppHF:
    def __init__(
        self,
        model_type: str,
        model_id: str,
        model_name: str,
        model_path: Optional[str] = None,
        repo_id: Optional[str] = None,
        filename: Optional[str] = None,
    ):
        self.model_type = model_type
        self.model_id = model_id
        self.model_name = model_name
        self.model_path = model_path
        self.repo_id = repo_id
        self.filename = filename

    def get_model(self):
        self.model = Whisper(self.filename)


    def transcribe(self, file_path, **kwargs) -> str:
        self.model.transcribe(file_path, 
                                diarize=False,
                                print_progress=False) 
    
class ModelHandler():
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
        self.get_model()
    
    def get_model(self):
        if self.model_name == "ggml-model-whisper-tiny.en-q8_0":
            self.model = ModelWhisperCppHF(**HF_MODELS_VOICE[self.model_name])
        else:
            raise ValueError(f"Model name {self.model_name} not supported.")
        self.model.get_model()

    def generate(self, file_path, **kwargs) -> str:
        self.model.transcribe(file_path, **kwargs)
        return self.model.model.output(output_srt=False, output_txt=False)
    
if __name__=="__main__":
    handler = ModelHandler("ggml-model-whisper-tiny.en-q8_0")
    result = handler.generate("data/output.wav")
    print(result)