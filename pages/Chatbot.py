import streamlit as st
from VirAsst.llm.llms import model_lists, ModelHandler
from VirAsst.template.templates import Template

# Sample available models
models = model_lists.keys()

# Sample tasks
tasks = ["Summarize", "Rephrase", "Fix Grammar", "Write Email", "Brainstorm", "Chat"]



# Function to create the ChatGPT-like interface
# Initialize session state if not already done


def chatbot():
    st.title("Chatbot")

    with st.sidebar:
        # Dropdown for model selection
        selected_model = st.sidebar.selectbox("Select Model:", models)

        # Selection box for tasks
        selected_task = st.sidebar.selectbox("Select Task:", tasks)


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

    # # Generate the response only after button click, and show the input box below
    # if 'latest_response' in st.session_state:
    #     st.info(f"Your input: {st.session_state['user_input']}")
    #     st.write(f"**Response:** {st.session_state['latest_response']}")


    # Text input for user message
    user_input = st.text_area("Enter your text here:", value=st.session_state['user_input'], key="user_input_area")

    # Button to submit the input
    if st.button("Submit"):
        if user_input:
            handler = ModelHandler(selected_model)



            # create query based on current input and conversation history
            # query = create_query(user_input, st.session_state['conversation'])
            query = Template().get_template(user_input, st.session_state['conversation'], selected_task)
            print(query)
            # Generate response using model and conversation history
            response = handler.model.generate(query)

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
            # st.info(f"Your input: {user_input}")
            # st.write(f"**Response:** {response}")
            # Rerun the script to update the conversation and move the input box below the response
            st.rerun()
        else:
            st.warning("Please enter some text!")

def create_query(input_text, conversation_history):
    # Create query based on current input and conversation history
    context = "\n".join([f"User: {msg['user']}\nBot: {msg['bot']}" for msg in conversation_history])
    return f"Context: {context}\n\nResponse to: {input_text}"


    

# # Run the interface
# if __name__ == "__main__":
#     chatbot()