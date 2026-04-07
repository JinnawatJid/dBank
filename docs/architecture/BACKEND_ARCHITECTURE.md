# Backend Architecture Overview

This document outlines the architectural decisions and industry-standard practices implemented in the Deep Insights Copilot backend. It serves as a guide for presenting the robustness, security, and scalability of the system, particularly within a corporate banking context.

## 1. Database Dependency Injection and Connection Pooling
**File:** `backend/db/session.py` and `backend/api/dependencies.py`

**What it is:**
We use FastAPI's `Depends` system to inject a database session into each API request that needs it. The connections are managed via a SQLAlchemy connection pool.

**Why it matters (The "Why" for your presentation):**
*   **Scalability:** Connection pooling reuses database connections instead of opening a new one for every request, which is crucial for handling high concurrency in production.
*   **Robust Session Management (Rollbacks):** When a request asks for a database session, we wrap it in a `try...except...finally` block. If an error occurs during the request, we execute a `db.rollback()`. This ensures that if a series of database operations fails halfway through, the database isn't left in an inconsistent state, and any incomplete transactions are safely aborted.
*   **Decoupling:** By injecting the dependency, endpoints do not need to know *how* to connect to the database, making the code much easier to unit test (we can inject a mock database).

## 2. Secure Configuration Management
**File:** `backend/core/config.py`

**What it is:**
We utilize `pydantic-settings` to manage and validate environment variables at application startup.

**Why it matters:**
*   **Fail-Fast Mechanism:** Instead of failing deep within the application logic when a required configuration (like a database password) is missing, the application crashes immediately upon startup, alerting operations teams immediately.
*   **Type Safety:** Pydantic ensures that ports are integers, booleans are booleans, etc., preventing subtle runtime bugs caused by string mismatches from environment variables.

## 3. Strict Validation for the Model Context Protocol (MCP) Server
**File:** `backend/mcp_server.py`

**What it is:**
The MCP server registers tools that the LLM can use. We upgraded the tool registration from flexible dictionaries to strict Pydantic models.

**Why it matters:**
*   **Defensive Programming:** In enterprise systems, data contracts must be strictly enforced. By using Pydantic to validate the JSON schema of the tools registered to the LLM, we ensure that the LLM always receives perfectly formatted tool definitions.
*   **Self-Documenting Code:** The Pydantic models clearly define what properties a tool must have (name, description, parameters), acting as living documentation.

## 4. API Versioning and Routing
**File:** `backend/main.py`

**What it is:**
All endpoints are now prefixed with `/api/v1` instead of living at the root (`/`).

**Why it matters:**
*   **Future-Proofing:** In a corporate setting, you will inevitably need to introduce breaking changes to APIs. Versioning (e.g., `/v1`, `/v2`) allows you to deploy new versions of an API without breaking existing integrations or frontends that rely on the older version.

## 5. Global Exception Handling
**File:** `backend/main.py`

**What it is:**
We implemented a centralized, global exception handler that catches any unhandled errors before they reach the user.

**Why it matters:**
*   **Security (No Information Leakage):** If a backend system crashes, it often spits out a stack trace containing internal file paths, database queries, or server configurations. A global exception handler catches these, logs them securely for the engineering team, and returns a sanitized, generic "500 Internal Server Error" to the client.
*   **Consistent API Contracts:** Frontends expect errors in a specific JSON format. Global handlers ensure that regardless of where or why an error occurs, the response always adheres to the expected structure.
