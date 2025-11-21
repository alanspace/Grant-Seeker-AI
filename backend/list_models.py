import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: No API Key found.")
else:
    genai.configure(api_key=api_key)
    print(f"Checking models for API Key: {api_key[:10]}...")
    
    try:
        print("\n--- AVAILABLE MODELS ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Name: {m.name}")
        print("------------------------")
    except Exception as e:
        print(f"Error listing models: {e}")