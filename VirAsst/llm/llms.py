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
from VirAsst.template.templates import Template
from VirAsst.rag.vectorDB import VectorDB
from VirAsst.modules import OpenAI_MODELS, HF_MODELS_TEXT, HF_MODELS_IMAGE, model_lists_image, model_lists_text
import json
from pathlib import Path



class ModelLlamaCppHF:
    def __init__(
        self,
        model_type: str,
        model_id: str,
        model_name: str,
        model_path: Optional[str] = None,
        repo_id: Optional[str] = None,
        filename: Optional[str] = None,
        n_ctx: Optional[int] = 2048,
    ):
        self.model_type = model_type
        self.model_id = model_id
        self.model_name = model_name
        self.model_path = model_path
        self.repo_id = repo_id
        self.filename = filename
        self.n_ctx = n_ctx

    def get_llm(self):
        self.llm = Llama.from_pretrained(
            repo_id=self.repo_id,
            filename=self.filename,
            n_ctx=self.n_ctx,
        )

    def is_online(self) -> bool:
        return self.repo_id is not None and self.filename is not None

    def generate(self, message, **kwargs) -> str:
        response = self.llm.create_chat_completion(messages=[{"role": "user", "content": message}])

        return response["choices"][0]["message"]["content"]
    
class ModelMoondream2(ModelLlamaCppHF):
    def get_llm(self):
        chat_handler = MoondreamChatHandler.from_pretrained(
                        repo_id="vikhyatk/moondream2",
                        filename="*mmproj*",
                    )
        self.llm = Llama.from_pretrained(
                        repo_id=self.repo_id,
                        filename=self.filename,
                        chat_handler=chat_handler,
                        n_ctx=self.n_ctx,
                    )
    
    def generate(self, message, image_url) -> str:
        response = self.llm.create_chat_completion(messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": message},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ]
            )

        return response["choices"][0]["message"]["content"]
    
class ModelLlava15(ModelLlamaCppHF):
    def get_llm(self):
        chat_handler = Llava15ChatHandler.from_pretrained(
                        repo_id=self.repo_id,
                        filename="*mmproj*",
                    )
        self.llm = Llama.from_pretrained(
                        repo_id=self.repo_id,
                        filename=self.filename,
                        chat_handler=chat_handler,
                        n_ctx=self.n_ctx,
                    )
    
    def generate(self, message, image_url) -> str:
        response = self.llm.create_chat_completion(messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": message},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ]
            )

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

    def generate(self, message, **kwargs) -> str:
        response = self.llm.invoke(message)

        return response.content
    
class ModelHandler():
    def __init__(self, model_name: str, model_type, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
        self.get_model()
    
    def get_model(self):
        if self.model_name == "gpt-4o":
            self.model = ModelOpenAI(**OpenAI_MODELS[self.model_name])
        elif self.model_name == "Llama-3.2-1B-Instruct-Q4_K_M-GGUF":
            self.model = ModelLlamaCppHF(**HF_MODELS_TEXT[self.model_name])
        elif self.model_name == "Moondream2":
            self.model = ModelMoondream2(**HF_MODELS_IMAGE[self.model_name])
        elif self.model_name == "Llava-1.5":
            self.model = ModelLlava15(**HF_MODELS_IMAGE[self.model_name])
        else:
            raise ValueError(f"Model name {self.model_name} not supported.")
        self.model.get_llm()

    def generate(self, previous_conversation, user_input, vectorstore_keyword="", **kwargs):
        if vectorstore_keyword != "":
            print(vectorstore_keyword)
            creator = VectorDB()
            creator.get_embedding(model_name="all-MiniLM-L6-v2.F16")
            creator.load_vectorDB(vectorstore_keyword)

            docs = creator.retrieve(user_input)
            context = ""
            for i in docs:
                context += i.page_content + " "
            contexto = context.replace("\n", "")
            query = Template().get_template(contexto, previous_conversation, context=contexto)
            return self.model.generate(query, **kwargs)
        else:
            # Create a query using the Template based on the user's input and conversation history
            query = Template().get_template(user_input, previous_conversation)

            return self.model.generate(query, **kwargs)

if __name__=="__main__":
    # model = ModelOpenAI(**OpenAI_MODELS["gpt-4o"])
    # model.get_llm()
    # print(model.generate("Hello, how are you?"))

    # model = ModelLlamaCppHF(**HF_MODELS["Llama-3.2-1B-Instruct-Q4_K_M-GGUF"])
    # model.get_llm()
    # print(model.generate("Hello, how are you?"))

    # handler = ModelHandler("gpt-4o")
    # print(handler.model.generate("Hello, how are you?"))

    # model = ModelHandler("Llama-3.2-1B-Instruct-Q4_K_M-GGUF")
    # print(model.model.generate("Hello, how are you?"))

    handler = ModelHandler("gpt-4o", model_type="text")
    user_input = "Hello, how are you?"
    conversation_store = {"conversation": []}
    image_url = ""
    vectorstore_keyword = "paper"

    response = handler.generate(user_input=user_input,
                                previous_conversation=conversation_store['conversation'],
                                      image_url=image_url, 
                                      vectorstore_keyword=vectorstore_keyword)
    print(response)