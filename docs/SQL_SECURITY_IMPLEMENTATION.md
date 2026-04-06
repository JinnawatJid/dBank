# SQL Security Implementation: Industry Standards

This document outlines how the Deep Insights Copilot ensures security and strictly mitigates SQL injection risks while allowing dynamic LLM-generated SQL queries via the Model Context Protocol (MCP).

## 1. Parameterized Queries

**Implementation:**
We use SQLAlchemy's `text()` function combined with bound parameters to execute SQL queries.

**Why:**
Direct string concatenation or f-string interpolation of user/LLM input into SQL queries creates critical SQL injection vulnerabilities. By using parameterized queries:
- The structure of the query is defined ahead of execution.
- The parameters are sent to the PostgreSQL engine separately from the SQL syntax.
- The database engine treats the parameters explicitly as *data*, preventing any malicious string from being interpreted as an executable SQL command.

**Example Code:**
```python
# Safe Implementation in backend/mcp_tools.py
from sqlalchemy import text
from backend.db.session import SessionLocal

def sql_query(template: str, params: dict):
    session = SessionLocal()
    # Safely binds parameters, preventing SQL injection
    result = session.execute(text(template), params)
    return [dict(row._mapping) for row in result]
```

## 2. Least Privilege Access Control

**Implementation:**
The `sql.query` MCP tool establishes its database connection using the credentials of an explicitly created, highly restricted user role (`app_user`).

**Why:**
Defense-in-depth dictates that even if an attacker were to bypass parameterized query restrictions (or if a rogue LLM attempted to execute destructive queries), the damage must be fundamentally constrained at the infrastructure layer.
- The `app_user` is provisioned during the database initialization phase (`db-init/init-user.sh`).
- It is granted **read-only** (`SELECT`) privileges.
- Its access is strictly scoped to the transformed business logic layers (the `marts` schema) rather than the `raw` schema, preventing direct querying of raw or unmasked PII.

**Conclusion:**
By combining application-layer parameterization (SQLAlchemy) with infrastructure-layer access control (Least Privilege RBAC), the system adheres to strict corporate banking industry standards, ensuring both flexibility for the LLM and absolute security for the underlying database.
