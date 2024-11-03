import base64
from io import BytesIO
import os

import pandas as pd
from PIL import Image
import streamlit as st

from utils.openai.functions import read_pdf, generate_ai_response_only_qa
from utils.logo import add_logo

st.set_page_config(page_title="Hackademix", page_icon="💡", layout="wide")

logo_data = add_logo()

st.markdown(
    f"""
    <style>
        [data-testid="stSidebarNav"] {{
            background-image: url(data:image/png;base64,{logo_data});
            background-repeat: no-repeat;
            padding-top: 120px;
            background-position: 20px 20px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom CSS
st.markdown("""
    <style>
    @font-face {
        font-family: 'MyCustomFont';
        src: url('C:/Users/i40012907/OneDrive - Endress+Hauser\Documents/venv_saad/azure_script/basel_hack_app/assets/E+H_SansBol.ttf') format('truetype'); /* Adjust the path and format according to your font files */
    }

    /* Apply the custom font to all text */
    body, .markdown-text-container, .css-18e3th9, h1, h2, h3, h4, h5, h6, .stButton>button, .stSelectbox, .stTextInput>div>div>input {
        font-family: 'MyCustomFont', sans-serif;
    }        

    /* Specific title color */
    .css-10trblm.e1fqkh3o2 {
        color: black !important; /* Set title color to black */
    }

    /* Create a blue strip at the top left */
    .blue-strip {
        position: fixed;
        top: 0;
        left: 0;
        width: 20px; /* Fixed width of 20px */
        height: 100%;
        background-color: #009EE3;
        z-index: 1000; /* Ensure it stays on top */
    }

    /* Set the background color */
    .reportview-container {
        background: #AFD3E8;
    }

    /* Set the font color for text and headers */
    .markdown-text-container, .css-18e3th9, h1, h2, h3, h4, h5, h6 {
        color: #00597A !important;
    }

    /* Set the title color to black */
    h1 {
        color: #000000 !important; /* Ensuring title is black */
    }

    /* Style the buttons */
    .stButton>button {
        background-color: #A8005C;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }

    /* Style the selectbox */
    .stSelectbox {
        color: #00597A !important;
    }

    /* Style the text input */
    .stTextInput>div>div>input {
        color: #00597A !important;
    }

    /* Adjust spacing and padding for a better layout */
    .stContainer {
        padding: 2rem;
    }
    </style>
    <div class="blue-strip"></div>
    """, unsafe_allow_html=True)

spinner_css = """
<style>
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.spinner {
  margin: 0 auto;
  border: 16px solid #f3f3f3; /* Light grey */
  border-top: 16px solid #3498db; /* Blue */
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 2s linear infinite;
}
</style>
"""


# Display custom spinner
def display_spinner(text):
    st.markdown(spinner_css, unsafe_allow_html=True)
    spinner_placeholder = st.empty()
    spinner_placeholder.markdown(f"""
    <div class="spinner"></div>
    <p style="text-align: center;">{text}</p>
    """, unsafe_allow_html=True)
    return spinner_placeholder


col1a, col2a, col3a = st.columns([2, 3, 2])

# with col2a:
#     #st.title('E+H Microsoft Office 365 Bot')
#     image = Image.open(r"C:\Users\i40012907\OneDrive - Endress+Hauser\Documents\venv_saad\azure_script\basel_hack_app\assets\EH_clipdrop-background-removal.png")#image = Image.open(r"/home/appuser/app/assets/your_main_page_img_here.png")
#     st.image(image, use_column_width=True)

col01, col02, col03 = st.columns([1, 8, 1])

with col02:
    st.title("📝📂 Research Q&A with Hackademix")

    # File uploader and supported formats information
    uploaded_file = st.file_uploader("Upload a File", type=['pdf', 'doc', 'docx', 'md', 'txt'])
    st.write("Supported formats: .pdf, .doc, .docx, .md, .txt")
    st.write("You can ask anything about the uploaded file.")
    st.write("Additionally, the Q&A bot provides a summary and key points about the file too.")

if 'qa_doc_messages' not in st.session_state:
    st.session_state.qa_doc_messages = []

# Read the uploaded file and store the document text in session state
if uploaded_file and uploaded_file.type == "application/pdf":
    document_text = read_pdf(uploaded_file)
    st.session_state.qa_doc_messages = [{"role": "user", "content": f"This is context data: {document_text}"}]
    st.success("Document uploaded and ready for Q&A.")

# Input area for user questions
question = st.text_input("Ask a question about the document", placeholder="Can you provide a summary?",
                         disabled=not uploaded_file)

if question and uploaded_file:
    # If this is the first question after uploading, use the document text as context
    if len(st.session_state.qa_doc_messages) == 1:  # Only the document text exists in session state
        # Generate the initial AI response using document text as context
        conversation_history = f"User: {st.session_state.qa_doc_messages[0]['content']}\n"

        # Add the question to the conversation history
        conversation_history += f"User: {question}\n"

        # Generate the AI response
        spinner_placeholder = display_spinner('Generating response...')
        response = generate_ai_response_only_qa(conversation_history, question)
        spinner_placeholder.empty()

        # Store the question and response in session state
        st.session_state.qa_doc_messages.append({"role": "user", "content": question})
        st.session_state.qa_doc_messages.append({"role": "assistant", "content": response})
    else:
        # For subsequent questions, use the last 8 messages for context
        conversation_history = f"User: {st.session_state.qa_doc_messages[0]['content']}\n"  # Always include context at index 0

        # Add the last 8 messages to conversation history
        for message in st.session_state.qa_doc_messages[1:][-8:]:
            role = "User: " if message["role"] == "user" else "Assistant: "
        conversation_history += f"{role}{message['content']}\n"

        # Add the latest question to the conversation history
        conversation_history += f"User: {question}\n"

        # Generate the response
        spinner_placeholder = display_spinner('Generating response...')
        response = generate_ai_response_only_qa(conversation_history, question)
        spinner_placeholder.empty()

        # Append the new question and response to session state
        st.session_state.qa_doc_messages.append({"role": "user", "content": question})
        st.session_state.qa_doc_messages.append({"role": "assistant", "content": response})

# Display the last 10 messages in the chat (excluding the context message at index 0)
for message in st.session_state.qa_doc_messages[1:][-9:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
