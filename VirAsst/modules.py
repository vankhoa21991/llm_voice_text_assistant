

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

HF_MODELS_TEXT = {
    "Llama-3.2-1B-Instruct-Q4_K_M-GGUF": {
        "model_name": "Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "model_id": "hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "model_type": "text",
        "model_path": "models/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "repo_id": "hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
        "filename": "llama-3.2-1b-instruct-q4_k_m.gguf",
    },
}

HF_MODELS_IMAGE = {
    "Llava-1.5":
    {
        "model_name": "Llava-1.5",
        "model_id": "mys/ggml_llava-v1.5-7b/q4_k",
        "model_type": "image",
        "model_path": None,
        "repo_id": "mys/ggml_llava-v1.5-7b",
        "filename": "*q4_k.gguf",
    },
}

HF_MODELS_VOICE = {
    "ggml-model-whisper-tiny.en-q8_0":
    {
        "model_name": "ggml-model-whisper-tiny.en-q8_0",
        "model_id": "ggml-model-whisper-tiny.en-q8_0",
        "model_type": "voice",
        "model_path": None,
        "repo_id": None,
        "filename": "models/ggml-tiny.en-q8_0.bin",
    },
}

model_lists_text = {
    "gpt-4o": OpenAI_MODELS,
    "Llama-3.2-1B-Instruct-Q4_K_M-GGUF": HF_MODELS_TEXT,
}

model_lists_image = {
    "Moondream2": HF_MODELS_IMAGE,
    "Llava-1.5": HF_MODELS_IMAGE,
}

embedding_list = {
     
     "all-MiniLM-L6-v2.F16": 
     {
            "model_path": "models/all-MiniLM-L6-v2.F16.gguf",
        }
}

model_lists_voice = {
    "ggml-model-whisper-tiny.en-q8_0": HF_MODELS_VOICE,
}