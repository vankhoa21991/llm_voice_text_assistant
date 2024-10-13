import streamlit as st
import requests
from VirAsst.llm.llms import model_lists_image, model_lists_text
from VirAsst.template.templates import tasks
import json

# FastAPI server URL (replace this with your actual FastAPI server URL if different)
API_URL = "http://127.0.0.1:8091"

def chatbot():
    st.title("Chatbot")

    with st.sidebar:
        # a dropdown for model type
        model_type = st.selectbox("Select Model Type:", ['text', 'image'])

        if model_type == 'text':
            model_lists = model_lists_text
        else:
            model_lists = model_lists_image

        # Dropdown for model selection
        selected_model = st.sidebar.selectbox("Select Model:", model_lists.keys())

        # Selection box for tasks
        selected_task = st.sidebar.selectbox("Select Task:", tasks)

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
                "selected_task": selected_task,
                "image_url": image_url
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
