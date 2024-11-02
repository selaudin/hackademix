import base64
from io import BytesIO
import os

import pandas as pd
from PIL import Image
import streamlit as st

from utils.openai.functions import call_faiss, generate_ai_response_and_data, generate_ai_response_only  # , extract_data_db
from utils.logo import add_logo

import time

st.set_page_config(page_title="HackademiX", page_icon="💡", layout="wide")

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
        src: url('assets/SansBol.ttf') format('truetype'); /* Adjust the path and format according to your font files */
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
#     with open("assets/hackademix_logo.png", "rb") as f:
#         st.image(f, use_column_width=True)

col01, col02, col03 = st.columns([2.5, 4, 2])

with col02:
    st.title('Research Assistant - MDPI')

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Input area for user questions
question = st.text_input("This is your personal Research Assistant", placeholder="Can you help me find a paper?",
                         disabled=False)

if question:
    # st.write('HI')
    if len(st.session_state.messages) == 0:
        # st.write('0')
        # Step 1: Get data from the database
        data = call_faiss(question)
        # st.write(data)

        # Step 2: Generate the AI response along with the original data
        spinner_placeholder = display_spinner('Generating initial response...')
        response, original_data = generate_ai_response_and_data(data, question)
        spinner_placeholder.empty()

        # Step 3: Store context data and the first response in session state
        st.session_state.messages.append({"role": "user", "content": f"this is context data: {original_data}"})
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        # For subsequent questions, use generate_ai_response_only with conversation history

        # Always include the original context message at the top
        conversation_history = f"User: {st.session_state.messages[0]['content']}\n"

        # Include the last 8 messages (excluding the original context)
        for message in st.session_state.messages[-8:]:
            role = "User: " if message["role"] == "user" else "Assistant: "
            conversation_history += f"{role}{message['content']}\n"

        # Add the latest question to the conversation history
        conversation_history += f"User: {question}\n"

        # Generate the response
        spinner_placeholder = display_spinner('Generating response...')
        response = generate_ai_response_only(conversation_history, question)
        spinner_placeholder.empty()

        # Append the new question and response to session state
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.messages.append({"role": "assistant", "content": response})

# Display the last 10 messages in the chat
for message in st.session_state.messages[1:][-9:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# user ask a question
# Approach 1
##function to retrieve data (give both data and paper selected)
##function which retain memory and answer next question based on previous interaction

##Approach 2