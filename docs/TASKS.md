# Task Checklist: Deep Insights Copilot

Use this file to track your progress during the 3-day sprint. Mark an `[x]` when a task meets its Definition of Done.

## Day 1: Data & Infrastructure

- [x] **Task 1.1: Environment Setup**
  - [x] Write `docker-compose.yml` defining a PostgreSQL service using the `pgvector/pgvector:pg15` image.
  - [x] Write a `requirements.txt` with base dependencies (fastapi, dbt-postgres, sqlalchemy, google-generativeai, etc).
  - *DoD: `docker-compose up -d db` runs successfully.*

- [x] **Task 1.2: Mock Data Generation**
  - [x] Write `scripts/generate_mock_data.py` (with timezone-aware TIMESTAMPTZ, audit `_ingested_at` columns, and Least Privilege access control).
  - [x] Generate 4 CSVs: `customers.csv`, `tickets.csv`, `logins.csv`, `products.csv`.
  - [x] Write a script or use `psql` to load these CSVs into the `raw` schema.
  - *DoD: Data is queryable in PostgreSQL under the `raw` schema.*

- [x] **Task 1.3: dbt Data Modeling**
  - [x] Run `dbt init dbank_analytics`.
  - [x] Create `models/staging/` and `models/marts/` directories.
  - [x] Write SQL for `fact_tickets`, `dim_customers`, `dim_products`.
  - [x] Add `schema.yml` with basic tests (unique, not_null).
  - *DoD: `dbt run` and `dbt test` complete without errors.*

- [x] **Task 1.4: Knowledge Base Processing (Enterprise-Grade Update)**
  - [x] Create `data/kb/` folder and write 5 Markdown files (e.g., "v1.2_release_notes.md", "login_issues.md").
  - [x] Implement schema creation and least-privilege RBAC in `db-init/init-kb-schema.sh` for reliable deployment.
  - [x] Write `scripts/embed_kb.py` to chunk text, utilizing structured Python `logging` instead of prints.
  - [x] Generate vectors using Google AI embeddings and insert them into `kb_embeddings` table using optimized `psycopg2.extras.execute_batch` inserts.
  - *DoD: `SELECT * FROM kb_embeddings LIMIT 1;` returns a valid vector.*

---

## Day 2: Backend & MCP

- [x] **Task 2.1: API Skeleton**
  - [x] Set up `backend/main.py` with FastAPI (using an enterprise folder structure: `core`, `api`, `db`).
  - [x] Create `POST /ask` endpoint accepting `{ "query": "string" }`.
  - [x] *Refactored: Implemented robust DB dependency injection (`db.rollback()`), global exception handling, and `/api/v1` versioning.*
  - *DoD: `/docs` Swagger UI is accessible and `/api/v1/ask` returns a dummy 200 response.*

- [x] **Task 2.2: Implement MCP Server Core**
  - [x] Create `backend/mcp_server.py`.
  - [x] Define the tool registry logic (functions that take parameters and return JSON).
  - [x] *Refactored: Upgraded tool schema registration to use strict Pydantic models for enterprise-grade validation.*
  - *DoD: You can programmatically call `list_tools()` and see 3 tools registered.*

- [x] **Task 2.3: Build Tools**
  - [x] Implement `sql.query(template, params)`. Ensure read-only user execution.
  - [x] Implement `kb.search(query)`. Execute cosine similarity SQL against `kb_embeddings`.
  - [x] Implement `kpi.top_root_causes()`. Execute specific aggregate SQL.
  - *DoD: Unit tests for all three tools pass (or manual testing confirms correct JSON output).*

- [x] **Task 2.4: LLM Orchestration & Guardrails**
  - [x] Integrate `google-generativeai` in the `/ask` route.
  - [x] Implement a loop: LLM generates response -> If tool requested, parse params -> Call MCP tool -> Send tool result back to LLM.
  - [x] Implement a basic regex or library for PII masking on tool outputs.
  - *DoD: Asking the API "What caused the v1.2 spike?" returns a valid natural language answer grounded in the database/KB.*

---

## Day 3: UI & DevOps

- [ ] **Task 3.1: Next.js UI**
  - [ ] Initialize Next.js project in `frontend/`.
  - [ ] Implement a chat interface component for user/assistant conversation.
  - [ ] Connect UI to `http://backend:8000/ask`.
  - [ ] Display an expandable section for "🛠️ Tool Logs" showing which MCP tools were used.
  - *DoD: You can chat with the AI through the browser on `localhost:3000`.*

- [ ] **Task 3.2: Dockerization**
  - [ ] Write `Dockerfile` for backend.
  - [ ] Write `Dockerfile` for frontend.
  - [ ] Update `docker-compose.yml` to include `backend` and `frontend` services.
  - *DoD: Running `docker-compose up --build` spins up the entire working system.*

- [ ] **Task 3.3: Final Checks & Submission**
  - [ ] Ensure `.env` is in `.gitignore` and create a `.env.example`.
  - [ ] Write `README.md` with instructions on how to start the app.
  - [ ] Create a ZIP file or verify the GitHub repo is accessible.
  - *DoD: Project is submitted to Joey.*
