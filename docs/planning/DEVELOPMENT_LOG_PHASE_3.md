# Development Log - Phase 3: UI Integration and Orchestration Fixes

This document outlines the troubleshooting and fixes applied during the End-to-End verification phase, specifically addressing the integration between the Next.js frontend, the FastAPI backend, and the Model Context Protocol (MCP) tool execution.

## 1. LLM Model Selection & Quota Issues

### 1.1 Migrating to `gemini-2.5-flash`
During initial E2E testing, the application encountered `404` errors with older models like `gemini-1.5-pro` (unsupported for the v1beta API version) and `429 Resource Exhausted` rate limit errors with other variants like `gemini-2.0-flash`.
* **Resolution:** We updated the `GEMINI_MODEL` default to `gemini-2.5-flash`. This model provides robust function-calling capabilities natively supported by the API and reliably circumvents the quota restrictions encountered on our current API key plan.

## 2. MCP Tool Orchestration Fixes

Integrating the Google Generative AI SDK (`google-generativeai==0.3.2`) with our custom MCP tool execution loop required resolving several critical incompatibility issues.

### 2.1 Tool Naming and Registration Mismatch
* **The Issue:** The Gemini SDK automatically sanitizes requested function names by replacing periods (`.`) with underscores (`_`). For example, the LLM requested `kpi_top_root_causes`, but our backend MCP server had the tool registered as `kpi.top_root_causes`. The simplistic replacement strategy (`replace("_", ".")`) failed because the original name contained both a dot and underscores. This resulted in a `ValueError: Tool 'kpi_top_root_causes' is not registered`.
* **The Fix:** We updated the adapter logic in `backend/api/routes.py` to iterate through the actual `mcp_server._tool_definitions`. It safely compares the LLM's sanitized string against the sanitized versions of the registered names, ensuring perfect dynamic mapping back to the original function name before execution.

### 2.2 SDK Function Response Formatting
* **The Issue:** When returning the result of an executed MCP tool back to the LLM (e.g., the JSON results of `kpi.top_root_causes`), the backend was using `genai.types.FunctionResponseDict`. However, in `google-generativeai==0.3.2`, this attribute does not exist, causing an `AttributeError`. A subsequent attempt to pass a raw dictionary resulted in unmarshaling errors where the SDK could not parse the structure.
* **The Fix:** We imported `google.ai.generativelanguage` (as `glm`) and replaced the dictionaries with strictly typed protobuf classes.
* **Implementation:** The response loop was refactored to wrap the result string in a `glm.FunctionResponse`, nested within a `glm.Part` and a `glm.Content` block. This strictly aligns with the expected gRPC contract for the v1beta SDK, allowing the LLM to successfully parse the tool's database result and generate a natural language summary.

## 3. End-to-End Success Criteria

With these fixes in place, the application successfully completed its first complete loop:
1. The user inputs a query via the Next.js UI.
2. The FastAPI backend receives the query, and the `gemini-2.5-flash` model interprets intent.
3. The model requests the `kpi.top_root_causes` tool.
4. The backend maps the name, executes the SQL against the PostgreSQL `marts` schema (using least-privilege `app_user` permissions), and retrieves ticket analytics.
5. The result is masked (PII replaced), formatted with `glm.Part`, and returned to the model.
6. The model synthesizes the analytics and sends a natural language summary back.
7. The React UI renders the summary and populates the "Tool Logs" dropdown.

The successful screenshot verification of this workflow indicates the core system is stable and ready for final infrastructure Dockerization.
