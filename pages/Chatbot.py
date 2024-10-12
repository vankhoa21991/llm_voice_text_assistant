import streamlit as st
from VirAsst.llm.llms import model_lists_image, model_lists_text, ModelHandler
from VirAsst.template.templates import Template, tasks
from PIL import Image
import io
import requests

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

        # Option to upload image file
        # uploaded_image = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])

        # Option to input image URL
        image_url = st.text_input("Enter Image URL:")

        # Display uploaded image or image from URL
        image_data = None  # To store image data to pass to handler
        # if uploaded_image is not None:
        #     # Open the uploaded image
        #     image = Image.open(uploaded_image)
        #     st.image(image, caption="Uploaded Image", use_column_width=True)

        #     # Convert image to bytes to pass to handler
        #     img_byte_arr = io.BytesIO()
        #     image.save(img_byte_arr, format='PNG')
        #     image_data = img_byte_arr.getvalue()

        if image_url:
            try:
                st.image(image_url, caption="Image from URL", use_column_width=True)

            except Exception as e:
                st.error(f"Error fetching image from URL: {e}")
                image_data = None


    if 'conversation' not in st.session_state:
        st.session_state['conversation'] = []

    # if 'user_input' not in st.session_state:
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
            handler = ModelHandler(selected_model, model_type=model_type)

            # create query based on current input and conversation history
            # query = create_query(user_input, st.session_state['conversation'])
            query = Template().get_template(user_input, st.session_state['conversation'], selected_task)
            print(query)
            # Generate response using model and conversation history
            response = handler.model.generate(query, image_url=image_url)

            # Save the conversation
            st.session_state['conversation'].append({
                'user': user_input,
                'bot': response
            })

            # Store the latest response to show after the input area
            # st.session_state['latest_response'] = response

            # Update the current input
            st.session_state['user_input'] = ""

            # Display current conversation
            st.success(f"Processing your request with model: **{selected_model}** for task: **{selected_task}**.")
            st.rerun()
        else:
            st.warning("Please enter some text!")

# def create_query(input_text, conversation_history):
#     # Create query based on current input and conversation history
#     context = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in conversation_history])
#     return f"Context: {context}\n\nResponse to: {input_text}"


    

# # Run the interface
if __name__ == "__main__":
    chatbot()