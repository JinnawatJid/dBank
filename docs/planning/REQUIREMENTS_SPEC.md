# Requirements Specification: Deep Insights Copilot

## 1. Executive Summary
**Project Name:** Deep Insights Copilot
**Objective:** Build an AI-powered Copilot for dBank's Operations Support team to reduce time spent on tickets by 80% and deflect 25% of repeat-question tickets.
**Core Capabilities:**
1. Answer natural-language questions grounded in dBank's internal knowledge base.
2. Run safe, parameterized queries (SQL, KPIs) securely via MCP (Model Context Protocol) tools.

---

## 2. Business Requirements
- **Goal 1:** Reduce time for Operations Support team by 80%.
- **Goal 2:** Deflect 25% of "repeat-question" tickets.
- **Goal 3:** Provide high confidence in AI answers by restricting it to read-only, parameterized queries and masking PII.

---

## 3. Functional Requirements

### 3.1 Data Ingestion & Storage (Data Layer)
- **Sources:** Ingest synthetic data for 4 domains: Customers, Tickets, Login Access, Products.
- **Storage:** Load data into PostgreSQL.
- **Modeling:** Transform data into a Star Schema (or 3NF) using **dbt**.
- **Quality:** Implement dbt data tests to ensure data integrity.

### 3.2 Knowledge Retrieval (Retrieval Layer)
- **Sources:** 5-10 short Markdown documents representing the Product Knowledge Base (known issues, conditions, policies, release notes).
- **Processing:** Chunk and embed the Markdown documents.
- **Storage:** Store embeddings in a vector database (PostgreSQL with `pgvector` extension).

### 3.3 Core LLM API (Backend / RAG)
- **Endpoint:** Expose a FastAPI endpoint (`/ask`) that accepts natural language questions.
- **LLM Integration:** Integrate with Google AI Studio.
- **RAG:** Retrieve relevant document context from pgvector to answer questions.
- **Tool Calling:** Route appropriate questions to MCP Tools.

### 3.4 MCP Server
- **Protocol:** Implement the Model Context Protocol (MCP) to standardize tool calling.
- **Tools Required:**
  1. `sql.query`: Executes read-only SQL against PostgreSQL with templated parameters.
  2. `kb.search`: Performs semantic search over the pgvector document store.
  3. `kpi.top_root_causes`: An aggregation helper tool to compute specific metrics.

### 3.5 User Interface (UI)
- **Platform:** Provide a UI built with Next.js for Operations Support to input questions and view answers + tool invocation logs.

---

## 4. Non-Functional Requirements (Guardrails & DevOps)

### 4.1 Security & Guardrails
- **Read-Only Access:** The database user utilized by the MCP server MUST have read-only permissions.
- **PII Masking:** Any PII in the database or logs must be masked or excluded from LLM context.
- **Parameterized Queries:** All SQL executed by the LLM must be parameterized to prevent SQL Injection.
- **Logging:** Every MCP tool call must be logged for auditing.

### 4.2 DevOps & Architecture ("Deployment-grade")
- **Containerization:** Entire application stack must be deployable via Docker (`docker-compose`).
- **CI/CD:** Basic GitHub Actions workflow to lint/test the codebase.
- **Observability:** Centralized or structured logging to track LLM response times, tool invocations, and errors.
- **Resilience:** Implement rate limits and basic circuit breakers for LLM API calls.
- **Secret Management:** Strict usage of `.env` files; no hardcoded credentials.

---

## 5. Acceptance Criteria

| Feature | Criteria |
|---------|----------|
| **Data Layer** | The PostgreSQL database contains tables for customers, tickets, logins, and products, transformed via dbt, passing all dbt tests. |
| **Vector Search** | The `kb.search` MCP tool successfully retrieves relevant markdown chunks based on semantic similarity using pgvector. |
| **RAG/LLM Answering** | Given the prompt "Did ticket volume spike after Virtual Bank App v1.2 release?", the system correctly queries the DB, correlates with KB docs, and provides an answer. |
| **SQL Tooling** | Given the prompt "Write the SQL for churned customers in the last 30 days", the LLM uses the `sql.query` tool safely with parameterized inputs. |
| **KPI Tooling** | Given the prompt "Top 5 root causes of product issues in the previous month", the LLM uses the `kpi.top_root_causes` tool to aggregate the data correctly. |
| **Security** | Attempting to execute `DROP TABLE customers` via the AI prompt fails cleanly due to read-only restrictions. |
| **Deployment** | Running `docker-compose up` successfully spins up the DB, FastAPI backend, MCP Server, and UI without manual intervention. |
