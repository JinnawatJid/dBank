from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import logging

import google.generativeai as genai

from backend.api.dependencies import get_db
from backend.mcp_server import mcp_server
from backend.api.mcp_gemini_adapter import convert_mcp_to_gemini_tools
from backend.core.security import pii_masker
from backend.core.config import settings

logger = logging.getLogger(__name__)

# Configure Google AI
genai.configure(api_key=settings.GOOGLE_API_KEY)

router = APIRouter()

class AskRequest(BaseModel):
    query: str

class AskResponse(BaseModel):
    answer: str
    tools_used: list[str] = []

@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    """
    Core endpoint to handle natural language questions using Google Generative AI
    and MCP tool orchestration.
    """
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == 'your_google_api_key_here':
        raise HTTPException(status_code=500, detail="Google API Key not configured properly.")

    try:
        # 1. Prepare Tools
        # In generativeai==0.3.2, tools are passed when initializing the GenerativeModel.
        tools = convert_mcp_to_gemini_tools(mcp_server._tool_definitions)
        model = genai.GenerativeModel(model_name='gemini-1.5-pro', tools=tools)

        # 2. Start Chat Session
        # The chat session manages the conversation history for us.
        chat = model.start_chat()

        tools_used = []
        max_turns = 5
        turn_count = 0

        # 3. Initial prompt
        system_prompt = "You are a helpful banking support assistant. Answer the user's questions by using the provided tools."
        current_input = f"{system_prompt}\nUser: {request.query}"

        # 4. Orchestration Loop
        while turn_count < max_turns:
            turn_count += 1

            # Send the message to the model
            response = chat.send_message(current_input)

            # Check if the model decided to call a function
            # In 0.3.2, function calls are usually in response.parts[0].function_call
            function_call = None
            if response.parts and hasattr(response.parts[0], 'function_call') and response.parts[0].function_call:
                function_call = response.parts[0].function_call

            if function_call:
                tool_name = function_call.name

                # Gemini replaces '.' with '_' in tool names, we need to map it back for mcp_server
                mcp_tool_name = tool_name.replace("_", ".")

                # Extract arguments as a dictionary
                # function_call.args is a protobuf Struct, we can cast it to dict
                tool_args = dict(function_call.args)

                logger.info(f"LLM requested tool: {mcp_tool_name} with args {tool_args}")
                tools_used.append(mcp_tool_name)

                try:
                    # Execute the tool
                    raw_result = mcp_server.execute_tool(mcp_tool_name, kwargs=tool_args)
                    result_str = json.dumps(raw_result, default=str)

                    # PII MASKING - Apply before returning to the LLM
                    masked_result_str = pii_masker.mask_text(result_str)

                    # Pass the masked result back to the model as a function_response
                    current_input = genai.types.ContentDict(
                        role="user",
                        parts=[
                            genai.types.PartDict(
                                function_response=genai.types.FunctionResponseDict(
                                    name=tool_name,
                                    response={"result": masked_result_str}
                                )
                            )
                        ]
                    )
                except Exception as e:
                    logger.error(f"Error executing tool {mcp_tool_name}: {e}")
                    # Send error back to LLM to retry
                    current_input = genai.types.ContentDict(
                        role="user",
                        parts=[
                            genai.types.PartDict(
                                function_response=genai.types.FunctionResponseDict(
                                    name=tool_name,
                                    response={"error": str(e)}
                                )
                            )
                        ]
                    )
            else:
                # No function call, the model generated a text response!
                return AskResponse(
                    answer=response.text,
                    tools_used=list(set(tools_used))
                )

        # If we reach here, we exceeded max turns
        return AskResponse(
            answer="I'm sorry, I couldn't find a complete answer after several attempts.",
            tools_used=list(set(tools_used))
        )

    except Exception as e:
        logger.error(f"Error in ask_question orchestration: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
