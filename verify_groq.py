import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)
api_key = os.getenv("GROQ_API_KEY")

print(f"Key loaded: {api_key[:10] if api_key else 'None'}...")

if api_key:
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        print("Groq Response:", chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")
else:
    print("No API Key found")
