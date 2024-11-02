import openai
import numpy as np
import pandas as pd
import faiss
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt 
from dotenv import load_dotenv
import os
import fitz

from utils.openai.prompt import get_prompt

# Load environment variables
load_dotenv()

# OpenAI API key
openai.api_key = os.getenv("API_KEY")


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_embeddings(text: str):
    response = openai.embeddings.create(
        input=text,
        model="gpt-4o"  # or "text-embedding-3-small" if available and appropriate
    )
    embeddings = response.data[0].embedding
    return embeddings

#func1 support vector search internall (call vector search) return both paper and answer

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_ai_response_and_data(data, question: str):
    completion = openai.chat.completions.create(
        model="gpt-4o",  # Use the appropriate model name, such as "gpt-4" for OpenAI
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Context: here's the data for context {data}. \
                Now this is the user's question: Question: {question}"
            }
        ],
        stream=True,  # Enable streaming if needed
        seed=0  # Add seed if applicable
    )
    # Extract the assistant's response from the first choice
    #answer = completion.choices[0].message['content']
    return completion, data

#func2, return only answer
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_ai_response_only(memory, question: str):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Context: here's the data for context {memory}. \
                Now this is the user's question: Question: {question}"
            }
        ],
        stream=True, seed=0)
    
    # Extract the assistant's response from the first choice
    #answer = response.choices[0].message['content']
    return response

def read_pdf(file):
    """Read and extract text from a PDF file-like object using PyMuPDF."""
    text = ""
    # Open the file-like object directly
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
    return text


