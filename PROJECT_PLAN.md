# 3-Day Project Plan: Deep Insights Copilot

This plan provides a strict, day-by-day roadmap to implement the "Deep Insights Copilot" from scratch, ensuring all requirements are met before the deadline.

---

## Day 1: Data Infrastructure & Retrieval Layer
**Goal:** Establish the foundation. Have a running database, mocked data, transformed schemas, and populated vector embeddings.

* **Morning (09:00 - 13:00): Environment & Mock Data**
  * Initialize git repository and set up `docker-compose.yml` (PostgreSQL + pgvector).
  * Write a Python script using `Faker` to generate raw CSV data (Customers, Tickets, Login Access, Products).
  * Load raw CSVs into a `raw` schema in PostgreSQL.

* **Afternoon (14:00 - 18:00): Data Modeling with dbt**
  * Initialize a dbt project (`dbt init`).
  * Create staging models (clean raw data).
  * Create mart models (Star Schema: `fact_tickets`, `dim_customers`, etc.).
  * Write and execute `dbt test` to ensure data integrity.

* **Evening (19:00 - 21:00): Knowledge Base & Embeddings**
  * Create 5-10 mock Markdown files simulating dBank product policies.
  * Write a Python script to chunk these files, generate embeddings via SentenceTransformers or Google AI API, and insert them into the `kb_embeddings` pgvector table.

---

## Day 2: Backend, MCP Server, & RAG Integration
**Goal:** Build the "brain" of the application. The system should be able to receive a question, use tools, and generate an answer.

* **Morning (09:00 - 13:00): FastAPI & Basic LLM Setup**
  * Set up FastAPI project structure (`main.py`, `routers/`, `models/`).
  * Create the `/ask` endpoint.
  * Integrate the Google AI Studio SDK and test a basic "Hello World" prompt.

* **Afternoon (14:00 - 18:00): MCP Server & Tools**
  * Implement the MCP Server specification.
  * Build Tool 1: `kb.search` (semantic search over pgvector).
  * Build Tool 2: `sql.query` (parameterized, read-only SQL execution).
  * Build Tool 3: `kpi.top_root_causes` (specific aggregation logic).

* **Evening (19:00 - 22:00): Orchestration & Guardrails**
  * Wire the FastAPI endpoint to standardly call the MCP tools via the LLM's tool-calling capabilities.
  * Implement PII masking logic before returning database results to the LLM context.
  * Test the Golden Dataset (defined in `TESTING_STRATEGY.md`) manually via API tools like Postman or Curl.

---

## Day 3: Frontend UI, DevOps, & Presentation Prep
**Goal:** Make it presentable, robust, and prepare for the interview.

* **Morning (09:00 - 12:00): Streamlit UI**
  * Build a simple Streamlit application.
  * Implement a chat interface.
  * Add a sidebar or expander to display "Tool Execution Logs" (this visually proves to interviewers that the MCP tools are working securely).

* **Afternoon (13:00 - 16:00): DevOps & Refinement**
  * Finalize `docker-compose.yml` to spin up the UI, API, MCP, and DB simultaneously.
  * Add a simple GitHub Actions workflow (`.github/workflows/ci.yml`) for basic linting/testing.
  * Clean up code, add docstrings, and ensure the `.env` template is clear.

* **Evening (17:00 - 20:00): Demo Prep & Submission**
  * Follow the `PRESENTATION_GUIDE.md`.
  * Record a dry-run of your 45-minute presentation.
  * Zip the project or finalize the GitHub repository link.
  * Submit the assignment via email to Joey.
