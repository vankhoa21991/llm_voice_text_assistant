import os
import io
import requests
from PIL import Image
from fastapi import FastAPI, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from VirAsst.llm.llms import model_lists_image, model_lists_text, ModelHandler
from VirAsst.template.templates import Template, tasks
from VirAsst.vectorDB import VectorDB, embedding_list

app = FastAPI()

# In-memory store for conversation history
conversation_store = {}

class ChatRequest(BaseModel):
    user_input: str
    model_type: str
    selected_model: str
    selected_task: str
    image_url: Optional[str] = None

class ChatResponse(BaseModel):
    user_input: str
    bot_response: str

@app.post("/chatbot", response_model=ChatResponse)
async def chatbot(request: ChatRequest):
    """Endpoint to process user input and generate chatbot response."""

    user_input = request.user_input
    model_type = request.model_type
    selected_model = request.selected_model
    selected_task = request.selected_task
    image_url = request.image_url

    # Initialize conversation if it doesn't exist
    if 'conversation' not in conversation_store:
        conversation_store['conversation'] = []

    # Add new user input to conversation history
    handler = ModelHandler(selected_model, model_type=model_type)

    # Create a query using the Template based on the user's input and conversation history
    query = Template().get_template(user_input, conversation_store['conversation'], selected_task)

    print(f"Query: {query}")
    print(f"Image URL: {image_url}")
    # Generate a response using the model handler
    response = handler.model.generate(message=query, image_url=image_url)

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
    creator = VectorDB(num_web=10, embedding_name=selected_embed)
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
    creator = VectorDB(num_web=10, embedding_name=selected_embed)
    creator.load_vectorDB(keyword)
    response = creator.retrieve(query)
    
    return {"message": "Documents retrieved successfully", "response": response}


@app.get("/get-embedding-list/")
async def get_embedding_list():
    return {"embeddings": list(embedding_list.keys())}