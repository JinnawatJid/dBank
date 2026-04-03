# Task Checklist: Deep Insights Copilot

Use this file to track your progress during the 3-day sprint. Mark an `[x]` when a task meets its Definition of Done.

## Day 1: Data & Infrastructure

- [ ] **Task 1.1: Environment Setup**
  - [ ] Write `docker-compose.yml` defining a PostgreSQL service using the `pgvector/pgvector:pg15` image.
  - [ ] Write a `requirements.txt` with base dependencies (fastapi, streamlit, dbt-postgres, sqlalchemy, google-generativeai, etc).
  - *DoD: `docker-compose up -d db` runs successfully.*

- [ ] **Task 1.2: Mock Data Generation**
  - [ ] Write `scripts/generate_mock_data.py`.
  - [ ] Generate 4 CSVs: `customers.csv`, `tickets.csv`, `logins.csv`, `products.csv`.
  - [ ] Write a script or use `psql` to load these CSVs into the `raw` schema.
  - *DoD: Data is queryable in PostgreSQL under the `raw` schema.*

- [ ] **Task 1.3: dbt Data Modeling**
  - [ ] Run `dbt init dbank_analytics`.
  - [ ] Create `models/staging/` and `models/marts/` directories.
  - [ ] Write SQL for `fact_tickets`, `dim_customers`, `dim_products`.
  - [ ] Add `schema.yml` with basic tests (unique, not_null).
  - *DoD: `dbt run` and `dbt test` complete without errors.*

- [ ] **Task 1.4: Knowledge Base Processing**
  - [ ] Create `data/kb/` folder and write 5 Markdown files (e.g., "v1.2_release_notes.md", "login_issues.md").
  - [ ] Write `scripts/embed_kb.py` to chunk text and generate vectors using Google AI embeddings.
  - [ ] Insert vectors into `kb_embeddings` table.
  - *DoD: `SELECT * FROM kb_embeddings LIMIT 1;` returns a valid vector.*

---

## Day 2: Backend & MCP

- [ ] **Task 2.1: API Skeleton**
  - [ ] Set up `backend/main.py` with FastAPI.
  - [ ] Create `POST /ask` endpoint accepting `{ "query": "string" }`.
  - *DoD: `/docs` Swagger UI is accessible and `/ask` returns a dummy 200 response.*

- [ ] **Task 2.2: Implement MCP Server Core**
  - [ ] Create `backend/mcp_server.py`.
  - [ ] Define the tool registry logic (functions that take parameters and return JSON).
  - *DoD: You can programmatically call `list_tools()` and see 3 tools registered.*

- [ ] **Task 2.3: Build Tools**
  - [ ] Implement `sql.query(template, params)`. Ensure read-only user execution.
  - [ ] Implement `kb.search(query)`. Execute cosine similarity SQL against `kb_embeddings`.
  - [ ] Implement `kpi.top_root_causes()`. Execute specific aggregate SQL.
  - *DoD: Unit tests for all three tools pass (or manual testing confirms correct JSON output).*

- [ ] **Task 2.4: LLM Orchestration & Guardrails**
  - [ ] Integrate `google-generativeai` in the `/ask` route.
  - [ ] Implement a loop: LLM generates response -> If tool requested, parse params -> Call MCP tool -> Send tool result back to LLM.
  - [ ] Implement a basic regex or library for PII masking on tool outputs.
  - *DoD: Asking the API "What caused the v1.2 spike?" returns a valid natural language answer grounded in the database/KB.*

---

## Day 3: UI & DevOps

- [ ] **Task 3.1: Streamlit UI**
  - [ ] Create `frontend/app.py`.
  - [ ] Implement `st.chat_message` loop for user/assistant conversation.
  - [ ] Connect UI to `http://backend:8000/ask`.
  - [ ] Display an `st.expander("🛠️ Tool Logs")` showing which MCP tools were used.
  - *DoD: You can chat with the AI through the browser on `localhost:8501`.*

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
