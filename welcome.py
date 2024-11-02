import openai
import streamlit as st
from utils.logo import add_logo
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# OpenAI API key
openai.api_key = os.getenv("API_KEY")

# Streamlit page configuration
st.set_page_config(page_title="HackademiX Chat", page_icon="💡", layout="wide")

# Add logo to sidebar
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

# Display a custom header and style
st.markdown(
    """
    <div class="blue-strip"></div>
    """,
    unsafe_allow_html=True,
)

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display ChatGPT-style conversation
st.title("Welcome to Hackademix Chat")

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if user_input := st.chat_input("Ask me anything about scholarly publications!"):
    # Display user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display response with a loading spinner
    with st.chat_message("assistant"):
        placeholder = st.empty()
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                ],
            )
            assistant_reply = response.choices[0].message["content"]
            placeholder.markdown(assistant_reply)
        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
