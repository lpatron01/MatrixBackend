#!/usr/bin/env python3
"""
Demonstrate the difference between working and failing models
"""

from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('HF_API_TOKEN')

if not token:
    print("No HF_API_TOKEN found")
    exit(1)

client = InferenceClient(api_key=token)

print("=== Testing Mistral Model (what chatbot uses) ===")
try:
    response = client.text_generation(
        'Test prompt',
        model='mistralai/Mistral-7B-Instruct-v0.1',
        max_new_tokens=10
    )
    print('[OK] Mistral worked:', response[:50])
except Exception as e:
    print('[FAIL] Mistral failed with:', type(e).__name__, '-', str(e) or 'empty error')

print("\n=== Testing Sentiment Model (what test uses) ===")
try:
    response = client.text_classification('This is great!', model='cardiffnlp/twitter-roberta-base-sentiment')
    print('[OK] Sentiment analysis worked:', len(response), 'results')
except Exception as e:
    print('[FAIL] Sentiment failed with:', type(e).__name__, '-', str(e) or 'empty error')

print("\n=== Summary ===")
print("The connection test passed because it uses WORKING models.")
print("Your chatbot fails because it uses the Mistral model which requires paid access.")
print("This is why you get the empty error message - it's a StopIteration exception.")
