import pytest
from unittest.mock import patch, MagicMock
from backend.mcp_tools import sql_query, kb_search, kpi_top_root_causes, SQLQueryInput, KBSearchInput

# --- Unit Tests with Mocked DB ---

@patch("backend.mcp_tools.SessionLocal")
def test_sql_query_success(mock_session_local):
    # Mock the SQLAlchemy session and execute method
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    # Mock the result of session.execute()
    mock_row = MagicMock()
    mock_row._mapping = {"id": 1, "name": "Test"}
    mock_session.execute.return_value = [mock_row]

    # Call the tool
    input_data = SQLQueryInput(template="SELECT * FROM test WHERE id = :id", params={"id": 1})
    result = sql_query(input_data)

    # Assertions
    assert result["status"] == "success"
    assert result["result"] == [{"id": 1, "name": "Test"}]
    # Now it's called 3 times: SET ROLE, the actual query, RESET ROLE
    assert mock_session.execute.call_count == 3
    mock_session.close.assert_called_once()

@patch("backend.mcp_tools.SessionLocal")
def test_sql_query_error(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    # Force an exception during execution
    mock_session.execute.side_effect = Exception("DB Connection Failed")

    input_data = SQLQueryInput(template="SELECT * FROM test")
    result = sql_query(input_data)

    assert result["status"] == "error"
    assert "DB Connection Failed" in result["message"]
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()

@patch("backend.mcp_tools._get_embedding")
@patch("backend.mcp_tools.SessionLocal")
def test_kb_search_success(mock_session_local, mock_get_embedding):
    # Mock embedding response
    mock_get_embedding.return_value = [0.1] * 768

    # Mock the SQLAlchemy session
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    # Mock the search result
    mock_row = MagicMock()
    mock_row.filename = "test.md"
    mock_row.content = "Test content"
    mock_row.similarity = 0.95
    mock_session.execute.return_value = [mock_row]

    # Call the tool
    input_data = KBSearchInput(query="How to login?", top_k=2)
    result = kb_search(input_data)

    # Assertions
    assert result["status"] == "success"
    assert len(result["result"]) == 1
    assert result["result"][0]["filename"] == "test.md"
    assert result["result"][0]["similarity"] == 0.95

    mock_get_embedding.assert_called_once_with("How to login?")
    mock_session.execute.assert_called_once()
    mock_session.close.assert_called_once()

@patch("backend.mcp_tools.SessionLocal")
def test_kpi_top_root_causes_success(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    # Mock KPI results
    mock_row1 = MagicMock()
    mock_row1._mapping = {"issue_type": "Login", "ticket_count": 10, "avg_resolution_time_hours": 1.5, "open_tickets": 2}
    mock_row2 = MagicMock()
    mock_row2._mapping = {"issue_type": "Billing", "ticket_count": 5, "avg_resolution_time_hours": 4.0, "open_tickets": 1}

    mock_session.execute.return_value = [mock_row1, mock_row2]

    result = kpi_top_root_causes()

    assert result["status"] == "success"
    assert len(result["result"]) == 2
    assert result["result"][0]["issue_type"] == "Login"
    assert result["result"][0]["ticket_count"] == 10

    mock_session.execute.assert_called_once()
    mock_session.close.assert_called_once()

# --- Integration Test Marker (optional) ---
# To run this: pytest backend/tests/test_mcp_tools.py -m integration
@pytest.mark.integration
def test_integration_kpi_tool():
    # This will actually hit the database configured in settings (e.g. localhost Docker DB)
    result = kpi_top_root_causes()
    # It should not fail, though the result might be empty if DB isn't seeded
    assert result["status"] in ["success", "error"]
    if result["status"] == "success":
        assert isinstance(result["result"], list)
