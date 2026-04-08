# Deployment-grade (DevOps & AI Systems): Study Guide for NotebookLM
*(Focus: Containerization, CI, Observability, Secret Hygiene, Rate Limits, Circuit Breakers, Cost & Safety)*

When moving an AI project from a "local prototype" to "Deployment-grade," especially in a banking context, DevOps principles must be rigorously applied. AI introduces new unpredictabilities (latency spikes, token costs, hallucinated tool calls) that traditional software doesn't face.

Here is the checklist of concepts required for the dBank MVP to be considered "Deployment-grade."

---

## 1. Containerization & CI (Continuous Integration)
**Containerization (Docker)**
*   **The Concept:** Ensure the application runs exactly the same way on the developer's laptop as it does on the CTO's laptop or the production server.
*   **dBank Implementation:** We use `docker-compose.yml` to orchestrate multiple independent services: the database (`db`), the initialization job (`db-init`), the FastAPI API (`backend`), and the Next.js UI (`frontend`).
*   **Best Practice (Least Privilege):** Good containerization means *not* running as `root`. Our Dockerfiles explicitly create `appuser` (for Python) and `nextjs` (for Node) to run the services. We also use isolated Docker networks (`frontend-network` vs `backend-network`) so the UI cannot physically talk to the database.

**CI (GitHub Actions)**
*   **The Concept:** Automated quality gates. Code shouldn't merge if it breaks the system.
*   **dBank Implementation:** We built a `.github/workflows/ci.yml` that automatically spins up a PostgreSQL container, generates mock data, runs the `dbt test` suite, and executes Python `pytest` suites every time code is pushed.

---

## 2. Resource/Secret Hygiene
**The Concept:** Never hardcode passwords, API keys (like Google Gemini keys), or database URIs into your code or push them to GitHub.
*   **dBank Implementation:** We use `.env` files locally (which are ignored by `.gitignore`). In code, we use tools like Python's `pydantic-settings` to strictly load and validate these environment variables at runtime. If a required secret is missing, the app refuses to start, preventing silent failures.

---

## 3. Observability (Specifically for AI)
**The Concept:** Traditional logging ("User clicked button") is not enough for LLMs. You need to observe the AI's "thought process" and tool usage.
*   **dBank Implementation:** We use **Structured JSON Logging**. Instead of printing text, we print JSON objects.
*   **Why JSON?** Because in production, logs are sent to systems like Datadog or Elasticsearch. JSON allows us to filter logs instantly (e.g., `SELECT * FROM logs WHERE event_type = 'tool_execution' AND tool_name = 'sql.query' AND execution_time_ms > 2000`). This is critical for auditing AI behavior.

---

## 4. Rate Limits & Circuit Breakers (API Resilience)
LLM APIs (like Google AI Studio or OpenAI) are notorious for rate limits (HTTP 429) or sudden internal crashes (HTTP 500).

*   **Rate Limits:**
    *   *The Problem:* The operation support team clicks "Ask" 50 times a second. The Google API blocks us, and the app crashes.
    *   *The Solution:* We must implement local rate limiting (e.g., using `slowapi` in FastAPI) to reject excessive user requests *before* we forward them to the expensive LLM API.
*   **Circuit Breakers:**
    *   *The Problem:* The Google API goes completely offline. If we keep sending requests, our backend threads will hang waiting for timeouts, eventually crashing our own server.
    *   *The Solution (The Circuit Breaker Pattern):* If the API fails 3 times in a row, the "circuit trips." For the next 60 seconds, our backend instantly returns a friendly error to the user ("AI service currently unavailable") *without* even trying to call Google. This protects our backend from resource exhaustion. In dBank, we implement this via robust `try/except` blocks handling specific `google.api_core.exceptions`.

---

## 5. Cost & Safety Controls
LLMs charge by the "token" (word fragments). Without controls, an AI system can bankrupt a company in a weekend.

*   **Cost Controls:**
    *   **Max Tokens:** We explicitly set `max_output_tokens` in the Gemini API configuration to prevent the LLM from generating infinite, rambling responses.
    *   **Max Turns (Orchestration Loop limit):** In our custom MCP routing, the LLM is allowed to execute tools in a loop (e.g., List tables -> Describe table -> Query table -> Fix SQL error -> Query again). We hardcode a `max_turns = 10` limit. If the LLM gets confused and enters an infinite loop of failing SQL queries, the system cuts it off at 10 to save money and CPU cycles.
*   **Safety Controls:**
    *   This circles back to the "AI Guardrails." We use parameterized MCP tools (no SQL injection) and PII masking. The safety control is the architectural guarantee that the AI is physically boxed into a read-only, masked environment.