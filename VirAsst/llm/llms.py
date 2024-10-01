from dotenv import load_dotenv
load_dotenv()
from typing import Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from typing import List, Dict, Optional
import time
from threading import Timer
from llama_cpp import Llama
from llama_cpp.llama_chat_format import (
    MoondreamChatHandler,
    MiniCPMv26ChatHandler,
    Llava15ChatHandler,
    Llava16ChatHandler,
)

import json
from pathlib import Path

OpenAI_MODELS = {
    "gpt-4o": {
        "model": "gpt-4o",
        "model_type": "text",
        "temperature": 0,
        "max_tokens": None,
        "timeout": None,
        "max_retries": 2,
    },
}

HF_MODELS = {
    "Llama-3.2-1B-Instruct-Q4_K_M-GGUF": {
        "model_name": "Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "model_id": "hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "model_type": "text",
        "model_path": "models/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "repo_id": "hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "filename": "*q4_k_m.gguf",
    },
}

model_lists = {
    "gpt-4o": OpenAI_MODELS,
    "Llama-3.2-1B-Instruct-Q4_K_M-GGUF": HF_MODELS,
}

class ModelLlamaCppHF:
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

    def get_llm(self):
        self.llm = Llama.from_pretrained(
            repo_id=self.repo_id,
            filename=self.filename,
            n_ctx=2048,
        )

    def is_online(self) -> bool:
        return self.repo_id is not None and self.filename is not None

    def generate(self, message) -> str:
        response = self.llm.create_chat_completion(messages=[{"role": "user", "content": message}])

        return response["choices"][0]["message"]["content"]

class ModelOpenAI:
    def __init__(
        self,
        model: str,
        temperature: int,
        max_tokens: int,
        timeout: int,
        max_retries: int,
        model_type: str = "text",
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.model_type = model_type

    def get_llm(self):
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout,
            max_retries=self.max_retries,
            # api_key="...",  # if you prefer to pass api key in directly instaed of using env vars
            # base_url="...",
            # organization="...",
            # other params...
        )

    def generate(self, message) -> str:
        response = self.llm.invoke(message)

        return response.content
    
class ModelHandler():
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
        self.get_model()
    
    def get_model(self):
        if self.model_name == "gpt-4o":
            self.model = ModelOpenAI(**OpenAI_MODELS[self.model_name])
        elif self.model_name == "Llama-3.2-1B-Instruct-Q4_K_M-GGUF":
            self.model = ModelLlamaCppHF(**HF_MODELS[self.model_name])
        else:
            raise ValueError(f"Model name {self.model_name} not supported.")
        self.model.get_llm()

if __name__=="__main__":
    # model = ModelOpenAI(**OpenAI_MODELS["gpt-4o"])
    # model.get_llm()
    # print(model.generate("Hello, how are you?"))

    # model = ModelLlamaCppHF(**HF_MODELS["Llama-3.2-1B-Instruct-Q4_K_M-GGUF"])
    # model.get_llm()
    # print(model.generate("Hello, how are you?"))

    handler = ModelHandler("gpt-4o")
    print(handler.model.generate("Hello, how are you?"))

    model = ModelHandler("Llama-3.2-1B-Instruct-Q4_K_M-GGUF")
    print(model.model.generate("Hello, how are you?"))