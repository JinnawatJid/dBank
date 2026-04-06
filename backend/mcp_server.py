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

        # Execute the function with the provided keyword arguments
        return self._tools[name](**kwargs)

# Create a singleton instance to be used across the application
mcp_server = MCPServerCore()

# --- Placeholder Tool Implementations for Task 2.2 DoD ---

def _dummy_sql_query(template: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    return {"status": "success", "result": "Dummy SQL result"}

def _dummy_kb_search(query: str) -> Dict[str, Any]:
    return {"status": "success", "result": "Dummy KB search result"}

def _dummy_kpi_root_causes() -> Dict[str, Any]:
    return {"status": "success", "result": "Dummy KPI result"}

# Register the tools required by Task 2.3
mcp_server.register_tool(
    name="sql.query",
    description="Executes a read-only SQL query.",
    parameters={"type": "object", "properties": {"template": {"type": "string"}}},
    func=_dummy_sql_query
)

mcp_server.register_tool(
    name="kb.search",
    description="Searches the knowledge base using vector similarity.",
    parameters={"type": "object", "properties": {"query": {"type": "string"}}},
    func=_dummy_kb_search
)

mcp_server.register_tool(
    name="kpi.top_root_causes",
    description="Retrieves aggregate KPIs for support ticket root causes.",
    parameters={"type": "object", "properties": {}},
    func=_dummy_kpi_root_causes
)

if __name__ == "__main__":
    # Quick visual check for the Definition of Done
    tools = mcp_server.list_tools()
    print(f"Registered Tools: {[t['name'] for t in tools]}")
