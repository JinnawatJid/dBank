# Presentation Slide Content Breakdown

This document provides a slide-by-slide outline of titles, bullet points, and suggested visuals for the 45-minute CTO presentation.

## Slide 1: Title Slide
*   **Title:** dBank: Enterprise Deep Insights Copilot
*   **Subtitle:** Secure, Agentic Data Exploration for Corporate Banking
*   **Presenter:** Jinnawat Jidsanoa - Mission Engineer Candidate
*   **Visual:** Clean, professional title layout with the dData/dBank logo.

## Slide 2: The Core Challenge in Enterprise AI
*   **Title:** The Friction of Enterprise LLM Deployment
*   **Bullet Points:**
    *   **The Promise:** LLMs offer unparalleled orchestration and natural language data exploration.
    *   **The Reality:** Highly regulated environments (Banking) have non-negotiable constraints on Data Privacy (PII) and Database Security (SQL Injection).
    *   **The Tension:** If we redact PII, the LLM can't search accurately. If we allow dynamic SQL, we risk systemic breaches.
*   **Visual:** A simple balance scale icon showing "AI Capabilities" on one side and "Enterprise Security" on the other.

## Slide 3: The dBank Solution Architecture
*   **Title:** Containerized, Secure-by-Design Architecture
*   **Bullet Points:**
    *   **Frontend (Next.js):** Modern, SSR-optimized chat interface.
    *   **Backend (FastAPI):** High-performance orchestration layer.
    *   **Model Context Protocol (MCP):** Isolated, typed tools for the LLM.
    *   **Unified Data Store (PostgreSQL + pgvector + dbt):** Single ACID-compliant database handling both relational data and vector embeddings.
*   **Visual:** Insert the high-level System Architecture Diagram (`docs/architecture/ARCHITECTURE.md` - Section 2).

## Slide 4: Innovation 1 - Reversible PII Masking
*   **Title:** Solving the Privacy Paradigm: Tokenization
*   **Bullet Points:**
    *   **Interception:** Microsoft Presidio detects standard and custom banking entities (e.g., `BANK_ACCOUNT`) *before* reaching the LLM.
    *   **Tokenization:** PII is replaced with UUID placeholders (e.g., `<PERSON_1>`).
    *   **Reversible Mapping:** An ephemeral in-memory dictionary maps tokens back to reality during tool execution.
    *   **Result:** The external LLM never processes raw PII, while maintaining exact-match query capabilities.
*   **Visual:** A step-by-step text flow: "Find John Doe" -> Masking -> "Find `<PERSON_1>`" -> LLM -> Tool Execution -> Unmasking.

## Slide 5: Innovation 2 - Defense in Depth SQL Execution
*   **Title:** Agentic Capabilities without Compromise
*   **Bullet Points:**
    *   **Least Privilege:** MCP server uses a restricted `app_user` role (Read-Only/SELECT).
    *   **Schema Segregation:** `app_user` only accesses the dbt-transformed `marts` schema, never raw data.
    *   **Parameterization:** SQLAlchemy `text()` strictly binds parameters, neutralizing SQL injection vectors from the LLM.
    *   **Input Guardrails:** Pydantic models validate all tool requests prior to DB interaction.
*   **Visual:** A padlock icon with concentric circles representing "Role Access", "Schema Isolation", and "Parameterization".

## Slide 6: Live System Demonstration
*   **Title:** dBank in Action
*   **Bullet Points:**
    *   **Scenario 1 (Unstructured RAG):** Querying internal policies via `pgvector` similarity search.
    *   **Scenario 2 (Structured SQL):** Dynamically querying aggregated ticket volumes.
    *   **Scenario 3 (Complex Orchestration):** Combining SQL data retrieval with PII masking and Knowledge Base synthesis.
*   **Visual:** Screenshot of the frontend UI showing an expandable "🛠️ Tool Logs" section.

## Slide 7: Technical Trade-offs & Future Scale
*   **Title:** Architectural Decisions & The Roadmap
*   **Bullet Points:**
    *   **PostgreSQL/pgvector vs. Dedicated Vector DB:** Chosen for ACID compliance and reduced operational overhead; Pinecone/Milvus considered for massive scale (>100M vectors).
    *   **dbt vs. Raw SQL Views:** Enforces software engineering practices (versioning, CI testing) on the data pipeline, resulting in cleaner LLM context.
    *   **Cloud LLM vs. Local Model:** Currently utilizing Gemma; production banking roadmap entails locally-hosted Llama 3 to guarantee absolute data residency.
*   **Visual:** A simple "Current vs. Future State" table.

## Slide 8: Q&A
*   **Title:** Questions & Discussion
*   **Bullet Points:**
    *   Thank you for your time!
*   **Visual:** Contact info / GitHub repository link.