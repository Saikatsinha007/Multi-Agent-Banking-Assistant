import os
from dotenv import load_dotenv
import google.generativeai as genai

# Force reload of .env
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")

print("--- API Key Check ---")
if not api_key:
    print("ERROR: GEMINI_API_KEY is not found in environment variables.")
else:
    print(f"Key loaded: {api_key[:10]}... (hidden)")
    
    print("\n--- Testing Gemini Connection ---")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello, can you hear me?")
        print("SUCCESS! Gemini responded:")
        print(response.text)
    except Exception as e:
        print("FAILURE! connection failed.")
        print(f"Error details: {e}")
