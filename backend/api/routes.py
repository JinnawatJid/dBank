from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import logging

import google.generativeai as genai
import google.ai.generativelanguage as glm

from backend.api.dependencies import get_db
from backend.mcp_server import mcp_server
from backend.api.mcp_gemini_adapter import convert_mcp_to_gemini_tools
from backend.core.security import pii_masker
from backend.core.guardrails import guardrail
from backend.core.audit import audit
from backend.core.config import settings
import uuid

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

    # Generate a unique session ID for audit logging
    session_id = str(uuid.uuid4())

    # Apply Reversible PII Masking to user input first to ensure we never log raw PII
    masked_query, pii_mapping = pii_masker.mask_text(request.query)

    # Check for Prompt Injection on the original query (or masked, depending on preference, but we log the masked one)
    is_injection, injection_msg = guardrail.detect_injection(request.query)
    if is_injection:
        audit.log_event("PROMPT_INJECTION_BLOCKED", session_id, {"masked_query": masked_query})
        raise HTTPException(status_code=400, detail=injection_msg)

    audit.log_event("USER_REQUEST", session_id, {"masked_query": masked_query})

    try:
        # 1. Prepare Tools
        # In generativeai==0.3.2, tools are passed when initializing the GenerativeModel.
        tools = convert_mcp_to_gemini_tools(mcp_server._tool_definitions)
        # Using a model that supports function calling (we try gemma-3-27b-it, or fallback to returning directly)
        model = genai.GenerativeModel(model_name='gemma-3-4b-it', tools=tools)

        # 2. Start Chat Session
        # The chat session manages the conversation history for us.
        chat = model.start_chat()

        tools_used = []
        max_turns = 5
        turn_count = 0

        # 3. Initial prompt
        system_prompt = "You are a helpful banking support assistant. Answer the user's questions by using the provided tools."
        current_input = f"{system_prompt}\nUser: {masked_query}"

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

                # Gemini replaces '.' with '_' in tool names, we need to map it back for mcp_server.
                # However, since mcp_server registers "kpi.top_root_causes" (which has an underscore AND a dot),
                # simply replacing all '_' with '.' breaks it. Let's find the original registered name.
                mcp_tool_name = tool_name
                for original_tool in mcp_server._tool_definitions:
                    if original_tool.name.replace(".", "_") == tool_name:
                        mcp_tool_name = original_tool.name
                        break

                # Extract arguments as a dictionary
                # function_call.args is a protobuf Struct, we can cast it to dict
                tool_args = dict(function_call.args)

                # UNMASK tool arguments before execution so DB can query real names
                unmasked_tool_args = {}
                for k, v in tool_args.items():
                    if isinstance(v, str):
                        unmasked_tool_args[k] = pii_masker.unmask_text(v, pii_mapping)
                    else:
                        unmasked_tool_args[k] = v

                logger.info(f"LLM requested tool: {mcp_tool_name} with args {tool_args}")
                audit.log_event("TOOL_EXECUTION_REQUEST", session_id, {
                    "tool": mcp_tool_name,
                    "masked_args": tool_args  # Log masked args for compliance
                })
                tools_used.append(mcp_tool_name)

                try:
                    # Execute the tool using UNMASKED args
                    raw_result = mcp_server.execute_tool(mcp_tool_name, kwargs=unmasked_tool_args)
                    result_str = json.dumps(raw_result, default=str)

                    # PII MASKING - Mask the database result before returning to the LLM
                    # We also update the mapping with any new PII found in the DB response
                    masked_result_str, new_mapping = pii_masker.mask_text(result_str)
                    pii_mapping.update(new_mapping)

                    audit.log_event("TOOL_EXECUTION_RESULT", session_id, {
                        "tool": mcp_tool_name,
                        "masked_result_preview": masked_result_str[:200]
                    })

                    # Pass the masked result back to the model as a function_response
                    current_input = glm.Content(
                        role="user",
                        parts=[
                            glm.Part(
                                function_response=glm.FunctionResponse(
                                    name=tool_name,
                                    response={"result": masked_result_str}
                                )
                            )
                        ]
                    )
                except Exception as e:
                    logger.error(f"Error executing tool {mcp_tool_name}: {e}")
                    # Send error back to LLM to retry
                    current_input = glm.Content(
                        role="user",
                        parts=[
                            glm.Part(
                                function_response=glm.FunctionResponse(
                                    name=tool_name,
                                    response={"error": str(e)}
                                )
                            )
                        ]
                    )
            else:
                # No function call, the model generated a text response!

                # We need to unmask the final text response before returning to the user
                final_answer = pii_masker.unmask_text(response.text, pii_mapping)

                audit.log_event("LLM_RESPONSE", session_id, {
                    "masked_answer": response.text,
                    "tools_used": list(set(tools_used))
                })

                return AskResponse(
                    answer=final_answer,
                    tools_used=list(set(tools_used))
                )

        # If we reach here, we exceeded max turns
        final_answer = "I'm sorry, I couldn't find a complete answer after several attempts."
        audit.log_event("LLM_RESPONSE_MAX_TURNS", session_id, {"masked_answer": final_answer})
        return AskResponse(
            answer=final_answer,
            tools_used=list(set(tools_used))
        )

    except Exception as e:
        logger.error(f"Error in ask_question orchestration: {e}", exc_info=True)
        if "Quota exceeded" in str(e) or "429" in str(e):
            return AskResponse(
                answer="I am currently experiencing high traffic and have hit an API rate limit. Please wait about 1 minute and try asking your question again.",
                tools_used=list(set(tools_used)) if 'tools_used' in locals() else []
            )
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
