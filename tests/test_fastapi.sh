curl -X POST "http://127.0.0.1:8091/chatbot" \
-H "Content-Type: application/json" \
-d '{
    "user_input": "Hello, what is machine learning?",
    "model_type": "text",
    "selected_model": "Llama-3.2-1B-Instruct-Q4_K_M-GGUF",
    "selected_task": "chat",
    "image_url": null
}'

curl -X POST "http://127.0.0.1:8091/chatbot" \
-H "Content-Type: application/json" \
-d '{
    "user_input": "Hello, what is in this image?",
    "model_type": "image",
    "selected_model": "Llava-1.5",
    "selected_task": "chat",
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
}'

# upload image
curl -X POST "http://127.0.0.1:8091/upload-image" \
-H "Content-Type: multipart/form-data" \
-F "file=@data/img.png"

curl -X POST "http://127.0.0.1:8091/create-vectordb/" \
-F "keyword=your_keyword_here" \
-F "additional_links=https://www.w3schools.com/python/python_intro.asp" \
-F "additional_links=https://www.w3schools.com/python/python_syntax.asp" \
-F "uploaded_files=@data/paper.pdf" \
-F "uploaded_files=@data/paper.pdf" \
-F "selected_embed=all-MiniLM-L6-v2.F16"
