import tempfile
import os
from io import BytesIO
import numpy as np
import pandas as pd
import faiss
import json
import fitz
from tenacity import retry, wait_random_exponential, stop_after_attempt

from utils.openai.prompt import get_prompt_basic, get_prompt_convo

import openai

from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("API_KEY")


def read_faiss():
    # read json
    with open('assets/paper_vector.json', 'r') as file:
        data1 = json.load(file)
    embeddings = [item['textVector'] for item in data1 if 'textVector' in item]
    embeddings = np.array(embeddings).astype('float32')
    embeddings.shape[1]

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, data1


def call_faiss(text: str):
    index, data1 = read_faiss()  # Load FAISS index and data
    query_embedding = generate_embeddings(text)
    query_embedding = np.array(query_embedding).astype('float32')
    query_embedding = query_embedding.reshape(1, -1)

    # Search for the closest matches in the index (top 2 results)
    distances, indices = index.search(query_embedding, 4)

    # Extract the data for the matched indices with the correct column names
    top_data = []
    for i in range(3):  # Iterate over the top 2 indices
        matched_index = indices[0][i]
    entry = {
        'file_name': data1[matched_index].get('file_name'),
        'text': data1[matched_index].get('text')
    }
    top_data.append(entry)

    return top_data


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_embeddings(text: str):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-large"  # or "text-embedding-3-small" if available and appropriate
    )
    embeddings = response.data[0].embedding
    return embeddings


# func1 support vector search internall (call vector search) return both paper and answer

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_ai_response_and_data(data, question: str):  # add prompt
    prompt = get_prompt_basic()
    completion = openai.chat.completions.create(
        model="gpt-4o",  # Use the appropriate model name, such as "gpt-4" for OpenAI
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {
                "role": "user",
                "content": f"Context: here's the data for context {data}. \
                Now this is the user's question: Question: {question}"
            }
        ],
        stream=False,  # Enable streaming if needed
        seed=0  # Add seed if applicable
    )
    # Extract the assistant's response from the first choice
    # answer = completion.choices[0].message.content
    return completion.choices[0].message.content, data
    # resp = 'this is for first answer from paper'
    # return resp, data


# func2, return only answer
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_ai_response_only(memory, question: str):  # add prompt
    prompt = get_prompt_convo()
    response = openai.chat.completions.create(
        model="gpt-4o",  # Use the appropriate model name, such as "gpt-4" for OpenAI
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {
                "role": "user",
                "content": f"Context: here's the data for context {memory}. \
                Now this is the user's question: Question: {question}"
            }
        ],
        stream=False, seed=0)

    # Extract the assistant's response from the first choice
    # answer = response.choices[0].message.content
    return response.choices[0].message.content
    # resp = 'this is for follow up question answer'
    # return resp


def extract_data_db(question):
    # embed = generate_embeddings(question)
    # this function will take embedding and search neo4j db for similar vectors
    # we need 1 NN for now
    # return None
    txt = 'first text from data db'
    return txt


def read_pdf(uploaded_file):
    # Use BytesIO to read the file as a file-like object
    pdf_data = BytesIO(uploaded_file.read())
    doc = fitz.open("pdf", pdf_data)  # Open as a PDF stream
    text = ""
    for page in doc:
        text += page.get_text()
    return text


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def generate_ai_response_only_qa(memory, question: str):  # add prompt
    prompt = get_prompt_convo()
    response = openai.chat.completions.create(
        model="gpt-4o",  # Use the appropriate model name, such as "gpt-4" for OpenAI
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {
                "role": "user",
                "content": f"Context: here's the data for context {memory}. \
                Now this is the user's question: Question: {question}"
            }
        ],
    stream=False, seed=0)

    # Extract the assistant's response from the first choice
    # answer = response.choices[0].message.content
    return response.choices[0].message.content
