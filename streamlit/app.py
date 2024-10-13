import streamlit as st
from pages.RAG import page_rag
from pages.Chatbot import chatbot
from pages.Diary import diary

# Inject CSS to hide the default Streamlit navigation and menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .css-18e3th9 {display: none;}  /* This will hide the sidebar navigation */
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Define the main function
def main():
    # Set the title of the app
    st.title("Personal Virtual Assistant")

    # Create a sidebar for navigation
    # st.sidebar.title("Navigation")
    pages = ["Main Page", "RAG", "LLM", "Diary"]

    # Check if 'page' is in session state, if not set it to 'Main Page'
    if 'page' not in st.session_state:
        st.session_state.page = pages[0]

    # # Create buttons to navigate between pages
    # for page in pages:
    #     if st.sidebar.button(page):
    #         st.session_state.page = page

    # Display the selected page
    if st.session_state.page == "Main Page":
        display_main_page()
    elif st.session_state.page == "RAG":
        page_rag()
    elif st.session_state.page == "LLM":
        chatbot()
    elif st.session_state.page == "Diary":
        diary()

# Function to display content for the main page
def display_main_page():
    st.header("Welcome to the Main Page!")
    st.write("This is the main page of the Streamlit demo.")
    st.write("Use the sidebar to navigate to other pages.")

# Run the main function
if __name__ == "__main__":
    main()