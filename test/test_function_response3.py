import google.generativeai as genai
import google.ai.generativelanguage as glm
from google.generativeai.types import content_types

try:
    part = glm.Part(
        function_response=glm.FunctionResponse(
            name="test",
            response={"result": "success"}
        )
    )
    print("Success")
except Exception as e:
    print(e)
