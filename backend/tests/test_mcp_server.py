import pytest
from backend.mcp_server import mcp_server

def test_mcp_server_list_tools():
    tools = mcp_server.list_tools()

    assert len(tools) == 3
    tool_names = [tool["name"] for tool in tools]
    assert "sql.query" in tool_names
    assert "kb.search" in tool_names
    assert "kpi.top_root_causes" in tool_names

def test_mcp_server_execute_tool():
    result = mcp_server.execute_tool("sql.query", {"template": "SELECT 1"})
    assert result["status"] == "success"
    assert result["result"] == "Dummy SQL result"

def test_mcp_server_execute_invalid_tool():
    with pytest.raises(ValueError, match="is not registered"):
        mcp_server.execute_tool("invalid_tool", {})
