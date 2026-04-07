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

    # Check for Prompt Injection on the original query
    is_injection, _ = guardrail.detect_injection(request.query)
    if is_injection:
        audit.log_event("PROMPT_INJECTION_BLOCKED", session_id, {"masked_query": masked_query})
        return AskResponse(
            answer=(
                "I'm sorry, but I'm not able to process that request. "
                "I'm designed exclusively to assist with dBank customer support inquiries, "
                "such as account questions, product information, and transaction support. "
                "Please ask me a question related to your banking needs."
            ),
            tools_used=[]
        )

    audit.log_event("USER_REQUEST", session_id, {"masked_query": masked_query})

    try:
        # 1. Prepare Tools
        # In generativeai==0.3.2, tools are passed when initializing the GenerativeModel.
        tools = convert_mcp_to_gemini_tools(mcp_server._tool_definitions)
        # Using a model that supports function calling
        system_instruction = (
            "You are an expert dBank customer support AI. Provide clear, concise answers formatted in markdown. "
            "CRITICAL RULES: Never explicitly mention the names of tools you use, never mention the filenames of the "
            "documents you read (e.g., 'login_issues.md'), and never explain your internal search process to the user. "
            "Present the final answer confidently as your own knowledge."
        )
        model = genai.GenerativeModel(
            model_name='gemma-4-31b-it', 
            tools=tools,
            system_instruction=system_instruction
        )

        # 2. Start Chat Session
        # The chat session manages the conversation history for us.
        chat = model.start_chat()

        tools_used = []
        # Allow enough turns for: schema exploration (2-3) + query retry (1-2) + final answer (1)
        max_turns = 10
        turn_count = 0

        # 3. Initial prompt
        # We only pass the user query here. The strict persona is handled by system_instruction.
        current_input = f"User: {masked_query}"

        # 4. Orchestration Loop
        while turn_count < max_turns:
            turn_count += 1

            # Send the message to the model
            response = chat.send_message(current_input)

            # Check if the model decided to call a function
            # Gemma models often put text reasoning in parts[0] and the function call in parts[1]
            function_call = None
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        break

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
                # Extract arguments as a dictionary safely unrolling Protobuf MapComposite objects
                def _unroll_proto(obj):
                    if hasattr(obj, 'items'):
                        return {k: _unroll_proto(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [_unroll_proto(i) for i in obj]
                    return obj
                
                tool_args = _unroll_proto(function_call.args)

                # UNMASK tool arguments recursively before execution so DB can query real names
                def _recursive_unmask(obj):
                    if isinstance(obj, str):
                        return pii_masker.unmask_text(obj, pii_mapping)
                    elif isinstance(obj, dict):
                        return {k: _recursive_unmask(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [_recursive_unmask(i) for i in obj]
                    return obj

                unmasked_tool_args = _recursive_unmask(tool_args)

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

                # Robustly extract text from all parts as Gemma 4 may return multiple text parts.
                # Often it returns reasoning in earlier parts and the final text in the last part.
                # To prevent leaking the model's internal thought process to the user, we should only
                # take the last text part.
                response_text = ""
                if response.parts:
                    text_parts = []
                    for part in response.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                    if text_parts:
                        response_text = text_parts[-1]

                # We need to unmask the final text response before returning to the user
                final_answer = pii_masker.unmask_text(response_text, pii_mapping)

                # --- DEFENSE-IN-DEPTH: OUTPUT PII GUARDRAIL ---
                # Industry standard: perform a final PII scan on the outbound response
                # BEFORE it is returned to the caller. Fail CLOSED — if PII is detected,
                # block the response entirely and raise a security audit event.
                detected_pii = pii_masker.scan_for_pii(final_answer)
                if detected_pii:
                    audit.log_event("OUTPUT_PII_BLOCKED", session_id, {
                        "reason": "PII detected in final LLM response before returning to user",
                        "detected_entity_types": detected_pii,
                        "tools_used": list(set(tools_used))
                    })
                    logger.warning(
                        f"OUTPUT GUARDRAIL TRIGGERED for session {session_id}. "
                        f"Detected PII types: {detected_pii}. Response blocked."
                    )
                    return AskResponse(
                        answer=(
                            "For data privacy and security reasons, I'm unable to display this information directly. "
                            "Customer contact details (email, phone number) are classified as personally identifiable "
                            "information (PII) and cannot be returned via this interface. "
                            "Please access customer records directly through the secure CRM portal."
                        ),
                        tools_used=list(set(tools_used))
                    )
                # --- END OUTPUT PII GUARDRAIL ---

                audit.log_event("LLM_RESPONSE", session_id, {
                    "masked_answer": response_text,
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
        if "Internal error encountered" in str(e) or "500" in str(e):
            return AskResponse(
                answer="The Google Generative AI API experienced an internal server error while processing the conversation. This can sometimes happen with the Gemma model's function calling feature. Please try asking your question again.",
                tools_used=list(set(tools_used)) if 'tools_used' in locals() else []
            )
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
