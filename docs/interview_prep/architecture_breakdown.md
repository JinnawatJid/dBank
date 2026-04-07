# dBank System Architecture Breakdown
**Target Audience:** CTO & Technical Panel
**Context:** This document provides a high-level technical breakdown of the dBank (Deep Insights Copilot) project, designed to be used as a reference during the architectural presentation.

---

## 1. Executive Summary
dBank is an enterprise-grade "Deep Insights Copilot" designed for corporate banking. It leverages Large Language Models (LLMs) to bridge the gap between natural language queries and complex backend data systems, while strictly adhering to data privacy and security standards.

The core value proposition is enabling users to interact seamlessly with both structured data (SQL databases) and unstructured data (Knowledge Base), orchestrated autonomously by an LLM, without compromising PII or system security.

---

## 2. Core Components

### 2.1 The Orchestration Layer (FastAPI Backend)
*   **Role:** The central nervous system. It receives user queries, orchestrates communication with the LLM (Google AI Studio via `gemma-4-31b-it`), manages conversation history, and handles tool execution.
*   **Why FastAPI?** High performance, native asynchronous support (crucial for IO-bound LLM/DB calls), and robust data validation via Pydantic.

### 2.2 The Presentation Layer (Next.js Frontend)
*   **Role:** The user interface. A modern chat interface built with Next.js App Router, TypeScript, and Tailwind CSS.
*   **Why Next.js?** Industry-standard React framework, server-side rendering capabilities, optimized build outputs (`standalone` mode), and strong typing for maintainability.

### 2.3 The Intelligence Layer (Google AI Studio & Gemma)
*   **Role:** The "brain". We use `gemma-4-31b-it` to parse user intent, decide which tools to call, and synthesize final natural language responses based on retrieved context.
*   **Integration:** Communicates via a structured Model Context Protocol (MCP) allowing dynamic tool calling.

### 2.4 The Execution Layer (Model Context Protocol - MCP)
*   **Role:** An independent server concept housing strict, typed tools that the LLM can invoke.
*   **Tools:**
    *   `sql.query`: Parameterized read-only execution.
    *   `kb.search`: Vector similarity search.
    *   `kpi.top_root_causes`: Pre-defined aggregated metrics.

### 2.5 The Data & Storage Layer (PostgreSQL, pgvector, dbt)
*   **Role:** The persistent state and analytical engine.
*   **Architecture:**
    *   **PostgreSQL:** The core relational database.
    *   **pgvector:** An extension to Postgres allowing it to act as a vector database for Knowledge Base embeddings, avoiding the need for a separate DB like Pinecone.
    *   **dbt (data build tool):** Transforms raw mock data into a clean, optimized "Star Schema" (marts) for efficient analytical querying by the AI.

---

## 3. Key Architectural Decisions & Innovations

### 3.1 Reversible PII Masking (Security & Privacy)
*   **The Problem:** We cannot send raw PII (like customer names or account numbers) to an external LLM, but the LLM *needs* those identifiers to instruct database searches.
*   **The Solution:** An interception layer using Microsoft Presidio.
    1.  **Mask:** Intercept user query, detect PII, and replace with a token (e.g., `<PERSON_1>`). Store a temporary in-memory map.
    2.  **Unmask (Tool Execution):** When the LLM requests a SQL query like `WHERE name = '<PERSON_1>'`, intercept the request, look up the map, and swap the real PII back in before hitting the DB.
    3.  **Remask (Tool Result):** Take DB results, apply tokens again, and feed to the LLM context.
    4.  **Final Unmask:** Intercept the LLM's final answer, replace tokens with actual PII, and return to the user.

### 3.2 Defense in Depth (Database Security)
*   **The Problem:** Allowing an LLM to generate SQL queries is inherently risky (SQL injection).
*   **The Solution:**
    1.  **Parameterized Queries:** Using SQLAlchemy `text()` with bound parameters ensures user input is never interpreted as executable code.
    2.  **Least Privilege:** The application connects via an `app_user` role that only has `SELECT` access, and *only* to the transformed `marts` schema—never the raw data.
    3.  **Pydantic Validation:** Strict input validation on all MCP tool calls drops malformed requests instantly.

### 3.3 Containerized Microservices
*   **The Architecture:** Docker Compose orchestrates `frontend`, `backend`, and `db` services.
*   **Network Isolation:** Uses separate networks (`frontend-network`, `backend-network`) ensuring the database is never exposed to the public internet or directly to the frontend container.
*   **Automated Initialization:** An ephemeral `dbank_dbt_init` service generates mock data and runs dbt transformations *before* the backend boots, ensuring data consistency on startup.

---

## 4. Why this matters to a CTO
This architecture is not just a prototype; it's designed with enterprise realities in mind:
*   **Compliance:** Reversible PII masking proves we understand regulatory constraints (GDPR/CCPA).
*   **Maintainability:** Strong typing, containerization, and separation of concerns (MCP from core API) mean the system can scale.
*   **Cost-Efficiency:** Utilizing PostgreSQL + pgvector eliminates the need (and cost) for an isolated, specialized vector database while maintaining performance.
