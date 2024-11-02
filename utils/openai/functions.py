from openai import OpenAI
import openai
import numpy as np
import pandas as pd
import faiss
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt 
from dotenv import load_dotenv
import os

from utils.openai.prompt import get_prompt

# Load environment variables
load_dotenv()

# OpenAI API key
openai.api_key = os.getenv("API_KEY")


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_embeddings(text: str):
    client = OpenAI(api_key=openai.api_key)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"  # or "text-embedding-3-small" if available and appropriate
    )
    embeddings = response.data[0].embedding
    return embeddings

#func1 support vector search internall (call vector search) return both paper and answer

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_ai_response_and_data(data, question: str):
    client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
    completion = client.chat.completions.create(
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
    client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
    response = client.chat.completions.create(
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