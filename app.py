import os
import io
import requests
from PIL import Image
from fastapi import FastAPI, Request, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import List, Optional
from VirAsst.llm.llms import ModelHandler
from VirAsst.rag.vectorDB import VectorDB
from VirAsst.voice.whisper import ModelHandler as VoiceModelHandler
from VirAsst.modules import model_lists_image, model_lists_text, model_lists_voice, embedding_list
import pyaudio
from ffmpeg import FFmpeg
from fastapi.responses import JSONResponse
import datetime

app = FastAPI()

# In-memory store for conversation history
conversation_store = {}

class ChatRequest(BaseModel):
    user_input: str
    model_type: str
    selected_model: str
    image_url: Optional[str] = None
    vectorstore_keyword: Optional[str] = None

class ChatResponse(BaseModel):
    user_input: str
    bot_response: str

# Model for response
class VoiceResponse(BaseModel):
    status: str
    message: str
    transcribed_text: Optional[str] = None
    processing_time: Optional[str] = None

@app.post("/chatbot", response_model=ChatResponse)
async def chatbot(request: ChatRequest):
    """Endpoint to process user input and generate chatbot response."""

    user_input = request.user_input
    model_type = request.model_type
    selected_model = request.selected_model
    image_url = request.image_url
    vectorstore_keyword = request.vectorstore_keyword

    # Initialize conversation if it doesn't exist
    if 'conversation' not in conversation_store:
        conversation_store['conversation'] = []

    # Add new user input to conversation history
    handler = ModelHandler(selected_model, model_type=model_type)

    
    print(f"User input: {user_input}")
    print(f"Image URL: {image_url}")
    print(f"Vectorstore keyword: {vectorstore_keyword}")
    # Generate a response using the model handler
    response = handler.generate(user_input=user_input,
                                previous_conversation=conversation_store['conversation'],
                                      image_url=image_url, 
                                      vectorstore_keyword=vectorstore_keyword)
    print(f"Bot response: {response}")
    # Save the conversation in the in-memory store
    conversation_store['conversation'].append({
        'user': user_input,
        'bot': response
    })

    # Return the chatbot response
    return ChatResponse(user_input=user_input, bot_response=response)

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Endpoint to handle image uploads."""
    print(f"Received file: {file.filename}")
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    # Process image as needed
    return {"message": "Image uploaded successfully."}

@app.get("/conversation")
async def get_conversation():
    """Retrieve the conversation history."""
    return conversation_store.get('conversation', [])

@app.post("/clear-conversation")
async def clear_conversation():
    """Clear the current conversation."""
    conversation_store['conversation'] = []
    return {"message": "Conversation cleared."}

@app.get("/")
async def root():
    return {"message": "Welcome to the Chatbot API!"}

@app.post("/create-vectordb/")
async def create_vector_db(
    keyword: str = Form(...),
    additional_links: List[str] = Form([]),
    uploaded_files: List[UploadFile] = File([]),
    selected_embed: str = Form("default_embedding")  # Choose a default embedding
):
    # Save uploaded files
    file_paths = []
    os.makedirs("uploaded_files", exist_ok=True)
    for uploaded_file in uploaded_files:
        file_path = os.path.join("uploaded_files", uploaded_file.filename)
        file_path = file_path.replace(" ", "_")
        with open(file_path, "wb") as f:
            f.write(await uploaded_file.read())
        file_paths.append(file_path)
    
    # Create VectorDB instance and process the data
    creator = VectorDB(num_web=10)
    creator.get_embedding(selected_embed)
    creator.create_vectorDB(keyword=keyword, 
                            additional_links=additional_links, 
                            localfiles=file_paths)
    
    return {"message": "VectorDB created successfully", "file_paths": file_paths}


@app.post("/retrieve-documents/")
async def retrieve_documents(
    keyword: str = Form(...),
    query: str = Form(...),
    selected_embed: str = Form("default_embedding")
):
    # Load and retrieve documents using VectorDB
    creator = VectorDB(num_web=10)
    creator.get_embedding(selected_embed)
    creator.load_vectorDB(keyword)
    response = creator.retrieve(query)
    
    return {"message": "Documents retrieved successfully", "response": response}


@app.get("/get-embedding-list/")
async def get_embedding_list():
    return {"embeddings": list(embedding_list.keys())}

@app.get("/get-model-list/{model_type}")
async def get_model_list(model_type: str):
    if model_type == "image":
        return {"models": model_lists_image}
    elif model_type == "text":
        return {"models": model_lists_text}
    else:
        return {"message": "Invalid model type. Please choose 'image' or 'text'."}

@app.get("/get-vectorstore/")
async def get_vectorstore():
    creator = VectorDB()
    # find all folder in vectorstore
    creator.vector_store_path = "vectorstore"
    vectorstore = os.listdir(creator.vector_store_path)

    return {"message": "Vectorstore retrieved successfully", 
            "vectorstore": vectorstore}

@app.get("/get-voice-model-list/")
async def get_voice_model_list():
    return {"models": model_lists_voice}

# Function to convert MP3 to WAV using ffmpeg
def ffmpegconvert(file_path):
    ffmpeg = FFmpeg().input(file_path).output("temp.wav", {
        "codec:a": "pcm_s16le",
        "ar": 16000,
        "ac": 1
    })
    ffmpeg.execute()

# Route to transcribe uploaded audio
@app.post("/transcribe/", response_model=VoiceResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    model_name: str = Form(...),
):
    file_location = f"temp_{file.filename}"
    
    # Save the uploaded file
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    
    try:
        # Handle MP3 files: convert to WAV
        if 'mp3' in file.filename:
            ffmpegconvert(file_location)
            file_location = "temp.wav"

        # Initialize the model handler (replace with actual handler)
        handler_voice = VoiceModelHandler(model_name)

        # Start transcription process
        start = datetime.datetime.now()
        result = handler_voice.generate(file_location)
        delta = datetime.datetime.now() - start
        
        return JSONResponse({
            "status": "success",
            "message": "Audio transcribed successfully!",
            "transcribed_text": result,
            "processing_time": str(delta)
        })

    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        })

    finally:
        # Clean up temporary files
        if os.path.exists(file_location):
            os.remove(file_location)
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")

