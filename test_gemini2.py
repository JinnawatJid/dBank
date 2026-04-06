import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

models_to_test = [
    "models/gemini-2.0-flash-lite-001",
    "models/gemini-1.5-pro",
    "models/gemini-pro",
    "models/gemma-3-4b-it"
]
for m in models_to_test:
    print(f"Testing {m}...")
    try:
        model = genai.GenerativeModel(m)
        response = model.generate_content("Hello")
        print(f"Success for {m}: {response.text}")
        break
    except Exception as e:
        print(f"Error for {m}: {e}")
