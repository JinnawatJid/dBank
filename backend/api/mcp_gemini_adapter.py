from typing import Any, Dict, List
from google.generativeai.types import content_types
from backend.mcp_server import ToolDefinition

def convert_mcp_to_gemini_tools(mcp_tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
    """
    Converts MCP tool definitions to the raw format accepted by older
    versions of google-generativeai, or passing JSON dict directly.
    In google-generativeai==0.3.2, tool calling was very basic or used raw dicts.
    """
    gemini_tools = []
    for tool in mcp_tools:
        # Replace '.' with '_' in function names because Gemini function names
        # usually only allow alphanumeric characters and underscores.
        safe_name = tool.name.replace(".", "_")

        func_decl = {
            "name": safe_name,
            "description": tool.description,
            "parameters": tool.parameters
        }
        gemini_tools.append(func_decl)

    # The actual structure is typically `{"function_declarations": [...]}`
    # wrapped in a Tool dict or list of dicts depending on API format.
    return [{"function_declarations": gemini_tools}]
