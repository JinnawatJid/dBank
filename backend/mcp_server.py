from typing import Any, Callable, Dict, List
from pydantic import BaseModel

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class MCPServerCore:
    """
    Model Context Protocol (MCP) Server Core
    Manages the registration and execution of tools that the LLM can invoke.
    """
    def __init__(self):
        # A dictionary mapping tool names to their executing functions
        self._tools: Dict[str, Callable] = {}
        # A dictionary holding the JSON Schema definitions for each tool
        self._tool_definitions: List[ToolDefinition] = []

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], func: Callable):
        """Registers a tool so the LLM knows it exists and how to use it."""
        # Use Pydantic model for strict validation
        tool_def = ToolDefinition(name=name, description=description, parameters=parameters)

        self._tools[name] = func
        self._tool_definitions.append(tool_def)

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns the list of registered tool definitions for the LLM prompt."""
        return [tool.model_dump() for tool in self._tool_definitions]

    def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> Any:
        """Executes a specific tool by name with the given arguments."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not registered.")

        func = self._tools[name]

        # Tools are defined in mcp_tools using Pydantic models (e.g. input_data: SQLQueryInput)
        # We need to map the dictionary `kwargs` to the expected Pydantic model.
        import inspect
        sig = inspect.signature(func)

        if len(sig.parameters) == 1 and "input_data" in sig.parameters:
            # Reconstruct the Pydantic model
            model_class = sig.parameters["input_data"].annotation
            input_data_instance = model_class(**kwargs)
            return func(input_data=input_data_instance)
        else:
            # Fallback for functions taking no args or unpacking kwargs directly
            return func(**kwargs)

# Create a singleton instance to be used across the application
mcp_server = MCPServerCore()

# --- Import Tool Implementations ---
from backend.mcp_tools import sql_query, kb_search, kpi_top_root_causes

# Register the tools required by Task 2.3
mcp_server.register_tool(
    name="sql.query",
    description="Executes a read-only SQL query with parameterized execution.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "template": {"type": "STRING", "description": "The SQL query to execute. Use :param_name for parameters."},
            "params": {"type": "OBJECT", "description": "Dictionary of parameters to bind to the query."}
        },
        "required": ["template"]
    },
    func=sql_query
)

mcp_server.register_tool(
    name="kb.search",
    description="Searches the knowledge base using vector similarity, returning top 5 results by default.",
    parameters={
        "type": "OBJECT",
        "properties": {
            "query": {"type": "STRING", "description": "The search query text."},
            "top_k": {"type": "INTEGER", "description": "Number of results to return (default 5)."}
        },
        "required": ["query"]
    },
    func=kb_search
)

mcp_server.register_tool(
    name="kpi.top_root_causes",
    description="Retrieves aggregate KPIs for support ticket root causes, including volume and average resolution time grouped by issue type.",
    parameters={"type": "OBJECT", "properties": {}},
    func=kpi_top_root_causes
)

if __name__ == "__main__":
    # Quick visual check for the Definition of Done
    tools = mcp_server.list_tools()
    print(f"Registered Tools: {[t['name'] for t in tools]}")
