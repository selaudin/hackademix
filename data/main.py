import os
import json
import tiktoken
import spacy
import fitz  # PyMuPDF

# Load the large English model in spaCy
nlp = spacy.load("en_core_web_lg")

# Define Tiktoken encoding (choose the model you are working with, e.g., "gpt-4")
encoding = tiktoken.get_encoding("cl100k_base")

dir_path = './articles_for_didi'
output = []

# Function to extract text from PDF using PyMuPDF
def extract_text_pymupdf(pdf_path): 
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda block: block[1])  # Sort blocks by vertical position
        for block in blocks:
            full_text += block[4] + " "  # block[4] is the text part of the block
    doc.close()
    return full_text.strip()  # Remove leading and trailing whitespace

# Loop through the directory and process each .json and corresponding .pdf file
for file_name in os.listdir(dir_path):
    if file_name.endswith('.json'):
        # Get file paths for JSON and PDF files
        json_file_path = os.path.join(dir_path, file_name)
        pdf_file_path = os.path.join(dir_path, file_name.replace('.json', '.pdf'))
        
        # Load JSON content for metadata
        with open(json_file_path, 'r') as json_file:
            content = json.load(json_file)
        
        # Extract and clean whole_text from the PDF
        whole_text = extract_text_pymupdf(pdf_file_path)
        whole_text = whole_text.replace("\n", " ")  # Replace newline characters with spaces
        
        # Process whole_text with spaCy to get lemmatized significant words
        doc_nlp = nlp(whole_text)
        filtered_tokens = [
            token.lemma_.upper() for token in doc_nlp
            if not token.is_stop and token.pos_ not in {"DET", "ADP", "AUX", "CCONJ", "ADJ", "PUNCT", "SPACE"}
        ]
        significant_words = " ".join(filtered_tokens)
        
        # Calculate token count of significant_words
        significant_words_tokens = encoding.encode(significant_words)
        significant_words_token_count = len(significant_words_tokens)
        
        # Create a structured dictionary for each document
        document = {
            "doc_name": file_name.replace('.json', ''),
            "content": content,  # JSON content as metadata
            "whole_text": whole_text,  # Text from PDF
            "significant_words": significant_words,
            "significant_words_token_count": significant_words_token_count
        }
        
        # Append this document structure to the output list
        output.append(document)

# Save the combined output to a new JSON file
with open('output.json', 'w') as output_file:
    json.dump(output, output_file, indent=4)

print("Combined JSON file created with structure: output.json")
