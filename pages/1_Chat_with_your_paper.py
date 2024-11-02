import base64
from io import BytesIO
import os
import streamlit as st
from utils.openai.functions import read_pdf, generate_ai_response_only
from utils.logo import add_logo

# Set page configuration and logo
st.set_page_config(page_title="HackademiX", page_icon="💾", layout="wide")
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

# Custom CSS for layout styling
st.markdown("""
    <style>
    .blue-strip { position: fixed; top: 0; left: 0; width: 20px; height: 100%; background-color: #009EE3; z-index: 1000; }
    body, .markdown-text-container, .css-18e3th9, h1, h2, h3, h4, h5, h6, .stButton>button, .stSelectbox, .stTextInput>div>div>input {
        font-family: 'Arial', sans-serif;
    }
    .reportview-container { background: #AFD3E8; }
    .stButton>button { background-color: #A8005C; color: white; border-radius: 12px; }
    </style>
    <div class="blue-strip"></div>
    """, unsafe_allow_html=True)

# Spinner function for visual feedback
spinner_css = """
<style>
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }}
.spinner { margin: 0 auto; border: 16px solid #f3f3f3; border-top: 16px solid #3498db; border-radius: 50%; width: 120px; height: 120px; animation: spin 2s linear infinite; }
</style>
"""
def display_spinner(text):
    st.markdown(spinner_css, unsafe_allow_html=True)
    spinner_placeholder = st.empty()
    spinner_placeholder.markdown(f"<div class='spinner'></div><p style='text-align: center;'>{text}</p>", unsafe_allow_html=True)
    return spinner_placeholder

# Page title and document upload section
st.title("📝 Document Q&A with Hackademix")
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

# Check if a file is uploaded and has content
if uploaded_file:
    # Check if file is non-empty
    uploaded_file.seek(0, os.SEEK_END)  # Move to the end of the file
    file_size = uploaded_file.tell()  # Get the file size
    uploaded_file.seek(0)  # Reset pointer to the beginning of the file

    if file_size > 0:
        try:
            # Read PDF content and save to session state
            document_text = read_pdf(uploaded_file)
            st.session_state.messages = [{"role": "user", "content": f"This is context data: {document_text}"}]
            st.success("Document uploaded and ready for Q&A.")
        except Exception as e:
            st.error(f"Failed to read the PDF file: {e}")
    else:
        st.warning("The uploaded file is empty. Please upload a valid PDF file.")
else:
    st.info("Please upload a PDF file to proceed.")

# Initialize session state for messages if not set
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Input area for user questions about the document
question = st.text_input("Ask a question about the document", placeholder="Can you provide a summary?", disabled=not uploaded_file)

# Process user questions and AI responses
if question and uploaded_file:
    conversation_history = f"User: {st.session_state.messages[0]['content']}\n"

    # Add context messages for continued conversation
    for message in st.session_state.messages[1:][-8:]:
        role = "User: " if message["role"] == "user" else "Assistant: "
        conversation_history += f"{role}{message['content']}\n"

    conversation_history += f"User: {question}\n"

    # Generate the AI response
    spinner_placeholder = display_spinner('Generating response...')
    response = generate_ai_response_only(conversation_history, question)
    spinner_placeholder.empty()

    # Update session state with new question and response
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat history in a user-friendly format
for message in st.session_state.messages[1:][-9:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Optionally display entire document text at the end for reference
if uploaded_file:
    st.text_area("Document Content", document_text, height=200, disabled=True)
