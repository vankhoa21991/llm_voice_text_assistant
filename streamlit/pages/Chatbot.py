import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()

# FastAPI server URL (replace this with your actual FastAPI server URL if different)
API_URL = os.getenv("API_URL")

def chatbot():
    st.title("Chatbot")

    with st.sidebar:
        model_type = st.selectbox("Select Model Type:", ["text", "image"])

        model_list = requests.get(f"{API_URL}/get-model-list/{model_type}")

        if model_list.status_code == 200:
            model_data = model_list.json().get("models", [])
            if isinstance(model_data, dict):
                # If the response is a list of models, just use it directly
                model_lists = model_data
            else:
                print("Unexpected response format. Expected a list.")
        else:
            print(f"Failed to retrieve model list: {model_list.status_code}")

        vectorstore_keywords = requests.get(f"{API_URL}/get-vectorstore/")
        if vectorstore_keywords.status_code == 200:
            vectorstore_keywords = vectorstore_keywords.json().get("vectorstore", "")
            if isinstance(vectorstore_keywords, list):
                vectorstore_keywords = [""] + vectorstore_keywords
            else:
                print("Unexpected response format. Expected a list.")
        else:
            print(f"Failed to retrieve vectorstore keyword: {vectorstore_keywords.status_code}")
        

        
        # Dropdown for model selection
        selected_model = st.sidebar.selectbox("Select Model:", model_lists.keys())

        # Select vectorstore keyword
        vectorstore_keyword = st.sidebar.selectbox("Select Vectorstore Keyword:", vectorstore_keywords)

        # Option to input image URL
        image_url = st.text_input("Enter Image URL:")

        # Display the image from URL
        if image_url:
            try:
                st.image(image_url, caption="Image from URL", use_column_width=True)
            except Exception as e:
                st.error(f"Error fetching image from URL: {e}")

    if 'conversation' not in st.session_state:
        st.session_state['conversation'] = []

    st.session_state['user_input'] = ""  # Stores the current input

    # Show the previous conversation
    if st.session_state['conversation']:
        st.subheader("Previous Conversation:")
        for i, convo in enumerate(st.session_state['conversation']):
            st.info(f"**User:** {convo['user']}")
            st.write(f"**Bot:** {convo['bot']}")
            st.write("---")  # Divider between messages

    # Text input for user message
    user_input = st.text_area("Enter your text here:", value=st.session_state['user_input'], key="user_input_area")

    # Button to submit the input
    if st.button("Submit"):
        if user_input:
            # Prepare payload for FastAPI
            payload = {
                "user_input": user_input,
                "model_type": model_type,
                "selected_model": selected_model,
                "image_url": image_url,
                "vectorstore_keyword": vectorstore_keyword
            }

            # Send the POST request to FastAPI's /chatbot endpoint
            response = requests.post(f"{API_URL}/chatbot", json=payload)

            if response.status_code == 200:
                bot_response = response.json()['bot_response']

                # Save the conversation in session state
                st.session_state['conversation'].append({
                    'user': user_input,
                    'bot': bot_response
                })

                # Update the current input
                st.session_state['user_input'] = ""

                # Refresh the app to display the updated conversation
                st.rerun()
            else:
                st.error(f"Error: {response.text}")
        else:
            st.warning("Please enter some text!")

    # Option to clear the conversation
    if st.button("Clear Conversation"):
        requests.post(f"{API_URL}/clear-conversation")
        st.session_state['conversation'] = []
        st.rerun()

if __name__ == "__main__":
    chatbot()
