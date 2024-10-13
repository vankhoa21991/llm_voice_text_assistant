import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import requests
import os

API_URL = os.getenv("API_URL")

def page_rag():
    if 'additional_inputs' not in st.session_state:
        st.session_state.additional_inputs = []

    # Function to add a new input row
    def add_input():
        st.session_state.additional_inputs.append("")

    with st.sidebar:
        st.sidebar.title("How to use")
        st.sidebar.markdown(
            """
            1. Enter the number of web references you want to use. (Max 20).
            2. Enter the keyword you want to generate a blog post for.
            3. Add links manually to the generated blog post.
            4. Click on the "Generate blog post" button.
            """
        )

        # Get embedding list from FastAPI
        embedding_response = requests.get(f"{API_URL}/get-embedding-list/")
        if embedding_response.status_code == 200:
            embedding_list = embedding_response.json().get("embeddings", [])
        else:
            embedding_list = []

        selected_embed = st.sidebar.selectbox("Select Embedding:", embedding_list)

        st.divider()
        st.sidebar.title("About")
        st.sidebar.markdown(
            """
            Content Generator allows you to generate SEO-optimized content from keywords. 
            It uses web references from top-ranking articles to generate your blog post. 
            """
        )

        st.divider()

        st.sidebar.title("FAQs")
        st.markdown(
            """
            #### How does it work?
            The Blog Post Generator uses web references from top-ranking articles to generate your blog post.
            """
        )

        st.divider()

    st.header("Let me help you with your documents!")
    st.title("Content Generator with RAG")

    keyword = st.text_input(label="Enter a keyword to search for", key="keyword", placeholder="")
    st.write("#### Add additional links:")

    # Add buttons for managing inputs
    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("+ Add More", on_click=add_input)
    with col2:
        st.button("Remove", on_click=lambda: st.session_state.additional_inputs.pop())

    for i, input_val in enumerate(st.session_state.additional_inputs):
        st.session_state.additional_inputs[i] = st.text_input(f"Input {i + 1}", value=input_val, key=f"input_{i}")

    st.write("#### Add additional PDF files:")
    os.makedirs("uploaded_files", exist_ok=True)

    uploaded_files = st.file_uploader("Upload multiple text files", type=["pdf"], accept_multiple_files=True)
    file_paths = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join("uploaded_files", uploaded_file.name.replace(" ", "_"))
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_paths.append(file_path)
            st.write(f"File saved at: {file_path}")

    submitted = st.button('✨ **Generate vectorDB**', type='primary')

    if submitted and not keyword:
        st.warning("Please enter a keyword", icon="⚠️")
    elif submitted:
        # Prepare files for FastAPI request
        files = [('uploaded_files', open(f, 'rb')) for f in file_paths]
        additional_links = st.session_state.additional_inputs

        # Make a POST request to the FastAPI create-vector-db endpoint
        response = requests.post(
            f"{API_URL}/create-vectordb/",
            data={"keyword": keyword, "additional_links": additional_links, "selected_embed": selected_embed},
            files=files
        )

        if response.status_code == 200:
            st.success("VectorDB created successfully", icon="🎉")
        else:
            st.error("Error creating VectorDB")

    # Retrieve documents
    query = st.text_input("Enter a query to search for", key="query", placeholder="")
    retrieve = st.button('✨ **Retrieve**', type='primary')

    if retrieve and not query:
        st.warning("Please enter a query", icon="⚠️")
    elif retrieve:
        # Make a POST request to the FastAPI retrieve-documents endpoint
        response = requests.post(
            f"{API_URL}/retrieve-documents/",
            data={"keyword": keyword, "query": query, "selected_embed": selected_embed}
        )

        if response.status_code == 200:
            documents = response.json().get("response", [])
            st.write("### Retrieved documents")
            st.write(documents)
            st.snow()
        else:
            st.error("Error retrieving documents")

if __name__ == "__main__":
    page_rag()