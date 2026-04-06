import os
import google.generativeai as genai
from google.generativeai.types import content_types
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    part = content_types.to_part({
        "functionResponse": {
            "name": "test",
            "response": {"result": "success"}
        }
    })
    print(part)
except Exception as e:
    print(e)
