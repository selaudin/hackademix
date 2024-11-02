import openai
import streamlit as st
import requests
import xmltodict
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
            try:
                # Extract scholarly keywords using ChatGPT-4
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an assistant skilled in identifying scholarly keywords. "
                                "Extract keywords that are specific, relevant to academic searches, and unique to the user's query. "
                                "Avoid common words or overly broad terms."
                            )
                        },
                        {"role": "user", "content": user_input},
                    ],
                )

                keywords = response.choices[0].message["content"]
                keywords = keywords.replace("\n", " ").strip()

                # Query arXiv API with extracted keywords
                arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{keywords}&start=0&max_results=3"
                arxiv_response = requests.get(arxiv_url)
                if arxiv_response.status_code == 200:
                    arxiv_data = xmltodict.parse(arxiv_response.content)
                    
                    # Check if 'entry' exists in the parsed data
                    if 'entry' in arxiv_data['feed']:
                        entries = arxiv_data['feed']['entry']
                        if not isinstance(entries, list):
                            entries = [entries]

                        # Display the first entry found
                        entry = entries[0]
                        link = entry['id'].replace('/abs/', '/pdf/')
                        title = entry.get('title', 'No title available')
                        summary = entry.get('summary', 'No summary available')

                        assistant_reply = f"**Title:** {title}\n\n**Summary:** {summary}\n\n**Link to Paper:** [Read Paper]({link})"
                    else:
                        assistant_reply = "No results found for your query. Try using different keywords."
                    
                    placeholder.markdown(assistant_reply)
                else:
                    placeholder.markdown("Failed to retrieve data from arXiv.")
                
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})

            except Exception as e:
                placeholder.markdown("An error occurred. Please try again.")
                st.session_state.messages.append({"role": "assistant", "content": "An error occurred. Please try again."})
