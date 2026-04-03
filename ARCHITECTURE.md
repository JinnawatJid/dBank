# Architecture Design: Deep Insights Copilot

## 1. System Overview

The Deep Insights Copilot is designed to be a robust, deployment-grade RAG (Retrieval-Augmented Generation) application. It bridges internal structured operational data and unstructured knowledge base documents, using Google AI Studio as the intelligence engine.

The architecture strictly adheres to the **Model Context Protocol (MCP)** to ensure AI tool-calling is standardized, logged, and isolated from core business logic.

---

## 2. High-Level Architecture Diagram

```mermaid
graph TD
    %% User and UI
    User([Operations Support]) --> UI[Streamlit UI]

    %% API & Orchestration
    UI -- "/ask (JSON)" --> FastAPI[FastAPI Backend\nRAG Orchestrator]

    %% LLM & MCP
    FastAPI -- "Prompt & Context" --> LLM[Google AI Studio]
    FastAPI -- "MCP Protocol" --> MCPServer[MCP Server]

    %% Tools inside MCP
    MCPServer --> Tool1(sql.query)
    MCPServer --> Tool2(kpi.top_root_causes)
    MCPServer --> Tool3(kb.search)

    %% Data Layer
    Tool1 -- "Read-Only SQL" --> PostgresDB[(PostgreSQL)]
    Tool2 -- "Read-Only SQL" --> PostgresDB
    Tool3 -- "pgvector similarity" --> PostgresDB

    %% Data Pipeline
    RawData[(Raw CSV/Mock Data)] --> dbt[dbt Core]
    KnowledgeBase[Markdown Files] --> Embedder[Embedding Script]

    dbt -- "Transform & Test" --> PostgresDB
    Embedder -- "Vectorize" --> PostgresDB

    %% Styling
    classDef ui fill:#4A90E2,color:white;
    classDef api fill:#50E3C2,color:black;
    classDef mcp fill:#F5A623,color:white;
    classDef db fill:#B8E986,color:black;

    class UI ui;
    class FastAPI api;
    class MCPServer mcp;
    class PostgresDB db;
```

---

## 3. Component Details

### 3.1 Data Pipeline (dbt + PostgreSQL)
- **Database:** PostgreSQL 15+ with the `pgvector` extension installed.
- **Data Loading:** Synthetic data generation scripts (Python/Faker) will generate raw data into schema `raw`.
- **dbt Transformations:** dbt will transform `raw` data into a dimensional **Star Schema** in the `analytics` schema to optimize for analytical queries by the AI.
  - **Fact Table:** `fact_tickets`
  - **Dimension Tables:** `dim_customers`, `dim_products`, `dim_login_access`
- **Data Tests:** dbt will run standard assertions (not null, unique, referential integrity).

### 3.2 Vector Store (pgvector)
- **Table Structure:** A table `kb_embeddings` storing `id`, `metadata` (filename, title), `content` (text chunk), and `embedding` (vector).
- **Ingestion:** A Python script utilizing SentenceTransformers (or Google Embeddings API) to chunk markdown files and insert vectors.

### 3.3 Core Backend (FastAPI)
- Acts as the orchestrator.
- Manages the conversation history.
- Communicates with Google AI Studio. It sends the user query, and if the LLM decides a tool is needed, FastAPI forwards the tool request to the MCP Server.

### 3.4 MCP Server
- Operates independently from the main business logic API.
- Registers three strict tools:
  - `sql.query`: Takes a parameterized query template and arguments. Executes as a restricted, read-only PostgreSQL user.
  - `kb.search`: Takes a search query, embeds it, and runs a cosine similarity search against `pgvector`.
  - `kpi.top_root_causes`: Executes pre-defined, hardened aggregate functions to ensure business metric consistency.

---

## 4. Sequence Diagram: Answering a User Query

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant LLM as Google AI Studio
    participant MCP as MCP Server
    participant DB as PostgreSQL (Data & Vector)

    User->>UI: "What caused the ticket spike for App v1.2?"
    UI->>API: POST /ask { "query": "..." }

    API->>LLM: Send Query + Available MCP Tools
    LLM-->>API: Tool Request: kb.search("App v1.2 issues")

    API->>MCP: Call Tool: kb.search
    MCP->>DB: pgvector cosine similarity search
    DB-->>MCP: Return Top 3 Markdown Chunks
    MCP-->>API: Tool Result (KB Chunks)

    API->>LLM: Send Query + Tool Result Context
    LLM-->>API: Tool Request: sql.query(ticket volume post v1.2)

    API->>MCP: Call Tool: sql.query
    MCP->>DB: Execute parameterized read-only query
    DB-->>MCP: Return aggregated ticket rows
    MCP-->>API: Tool Result (Ticket Data)

    API->>LLM: Send Query + KB Context + SQL Context
    LLM-->>API: Final Natural Language Answer

    API-->>UI: Return Answer
    UI-->>User: Display Answer & Tool Execution Logs
```

---

## 5. Security & Deployment Strategy

- **Database Roles:**
  - `dbt_user`: Owner of tables, can DDL/DML.
  - `app_user`: Read-only access to `analytics` and `kb_embeddings` schemas only. Masked PII views are exposed to `app_user`.
- **Infrastructure as Code:**
  - `docker-compose.yml` defining services: `db`, `backend`, `mcp-server`, `frontend`.
- **Observability:**
  - Use Python's `logging` module to output JSON-structured logs to stdout.
  - Docker daemon will capture these logs.
- **Resilience:**
  - `Tenacity` library used in FastAPI for retry-mechanisms with exponential backoff when calling Google AI Studio.
