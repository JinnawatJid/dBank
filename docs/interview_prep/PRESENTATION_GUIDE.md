# dData Mission Engineer Interview: Presentation Guide

**Candidate:** Jinnawat Jidsanoa
**Audience:** CTO & Technical Panel
**Time:** 45 minutes (Presentation + Demo) + 15 minutes Q&A

---

## 1. Introduction & Context Setting (5 minutes)

**Objective:** Hook the CTO. Briefly set the stage and immediately establish that you approached this like an engineering lead, not just a junior dev writing scripts.

*   **Greeting:** "Thank you for the opportunity to present today. I'm excited to walk you through the Deep Insights Copilot."
*   **The Business Problem:** "The core objective was clear: reduce the Operations Support team's ticket resolution time by 80% and deflect 25% of repeat queries. They needed an intelligent, conversational layer on top of their corporate banking data."
*   **The Approach (The "How"):** "When I received this assignment, my first step wasn't coding—it was planning. I structured this as a rigorous 3-day sprint. You can see this structured approach in my `PROJECT_PLAN.md`. I treated this not as a prototype, but as an MVP destined for production in a highly regulated banking environment."
*   **Key Themes:** Mention that your architecture prioritizes three things: **Accuracy, Security (Defense-in-Depth), and Observability.**

---

## 2. Architecture Walkthrough (10 minutes)

**Objective:** Prove your technical depth. Use the `CTO_PRESENTATION.md` as your guide here. (If you have a slide or a diagram, show it here).

*   **The Tech Stack:**
    *   **Data Transformation:** "I chose dbt to transform raw data into a clean Star Schema. This ensures data integrity before the LLM even sees it."
    *   **Vector Database:** "For the RAG (Knowledge Base) implementation, I leveraged PostgreSQL with the `pgvector` extension. This keeps our relational and vector data within the same ecosystem, reducing infrastructure complexity."
    *   **Backend & LLM Integration:** "FastAPI handles the backend, integrating with Google AI Studio. I built a custom implementation of the Model Context Protocol (MCP)."
*   **Deep Dive - Security & Zero-Trust:** (This is crucial for a CTO audience)
    *   "In a banking context, we can't just trust an LLM to generate raw SQL. I implemented a strict Model Context Protocol."
    *   **Pydantic:** "All tool inputs are validated via Pydantic. If the LLM hallucinates an argument, the validation fails gracefully."
    *   **Parameterized Queries:** "Direct string formatting for SQL is strictly prohibited to prevent SQL injection. We use SQLAlchemy parameterized queries."
    *   **Least Privilege:** "The database connection strictly enforces least privilege (`SET ROLE app_user;`). The LLM can only query read-only, PII-masked marts, and every execution is wrapped in a `try/except/finally` block with explicit rollbacks to maintain transactional integrity."

---

## 3. The Execution & Post-Mortem Highlights (10 minutes)

**Objective:** Show that you can navigate complex engineering problems and learn from failure. Refer heavily to your `POST_MORTEM.md`.

*   **Transition:** "Planning is great, but execution is where the real engineering happens. I encountered several complex challenges and documented them in my Post-Mortem."
*   **Highlight 1 - The Vector Dimension Trap:** "For instance, I initially hit a dimension mismatch error migrating to a newer embedding model (768 vs 3072 dimensions). I quickly realized the schema was statically bound and resolved it by updating the pgvector initialization script."
*   **Highlight 2 - PII Masking & Nested Payloads:** "I built a reversible PII masking system to protect data before it hits the LLM. However, I discovered a bug where nested Protobuf objects returned by the LLM caused silent query failures because the unmasking loop wasn't recursive. I had to build a custom unrolling function to deep-traverse and safely unmask nested parameters."
*   **Highlight 3 - Defense-in-Depth:** "Finally, I realized protecting data *going to* the LLM wasn't enough. I implemented an 'Output PII Guardrail' that scans the final response before it's sent to the user. If PII is detected, it fails closed, logs a security warning, and directs the user to the CRM. This is the essence of Defense-in-Depth."

---

## 4. Live Demo (15 minutes)

**Objective:** Show the working system. Move smoothly and explain *what* the system is doing behind the scenes.

*   **Setup:** Have `docker-compose up` already running.
*   **Scenario 1: Knowledge Base (RAG)**
    *   **Action:** Ask a question like, "Did ticket volume spike after Virtual Bank App v1.2 release?"
    *   **Talking Point:** While it generates, explain: "Here, the system is utilizing the `kb.search` MCP tool. It's querying the pgvector database for semantic similarity against our embedded Markdown policies."
*   **Scenario 2: Secure SQL Query**
    *   **Action:** Ask, "Write the SQL for churned customers in the last 30 days."
    *   **Talking Point:** "Notice the tool execution logs. The LLM decided to use the `sql.query` tool. It passed parameterized inputs, and the backend executed it safely."
*   **Scenario 3: KPI Aggregation**
    *   **Action:** Ask, "What are the top 5 root causes of product issues?"
    *   **Talking Point:** "This utilizes a specific `kpi.top_root_causes` tool, demonstrating how we can encapsulate complex business logic into distinct, manageable tools rather than relying on the LLM to write complex SQL aggregations on the fly."

---

## 5. Conclusion & Future Scale (5 minutes)

**Objective:** Wrap up strong and show forward-thinking.

*   "To summarize, we achieved a secure, robust MVP that proves the viability of an LLM-driven Copilot for operations."
*   **Future Improvements:** "If we were scaling this to production next week, I would focus on:
    1.  **Caching Layer:** Implementing Redis to cache frequent queries.
    2.  **Advanced Observability:** Integrating OpenTelemetry to trace tool execution times.
    3.  **Agentic Frameworks:** Perhaps transitioning the custom MCP routing to a mature framework like LangGraph for more complex, multi-step reasoning."
*   "Thank you. I'm happy to dive into any part of the architecture or code."
