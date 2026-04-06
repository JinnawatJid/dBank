import google.generativeai as genai
from google.generativeai.types import content_types

try:
    content = content_types.to_content([
        {
            "functionResponse": {
                "name": "test",
                "response": {"result": "success"}
            }
        }
    ])
    print("Success")
except Exception as e:
    print(e)

try:
    content = content_types.to_content(genai.types.PartDict(function_response={"name": "test", "response": {"result": "ok"}}))
    print("Success 2")
except Exception as e:
    print(e)
