# CTO Presentation Script: dBank Deep Insights Copilot

**Total Time Allocated:** 45 Minutes
**Format:** Live Presentation + Architecture Walkthrough + Live Demo
**Audience:** CTO & Technical Panel

---

## Part 1: Introduction & The Problem Statement (5 Minutes)

**[Slide 1: Title Screen - dBank Deep Insights Copilot]**
*   **Speaker:** "Good morning/afternoon. Thank you for the opportunity to present today. I'm Jinnawat Jidsanoa, and I'm excited to walk you through 'dBank'—a Deep Insights Copilot designed for the corporate banking sector."

**[Slide 2: The Core Challenge in Enterprise AI]**
*   **Speaker:** "When we look at deploying Large Language Models in highly regulated industries like banking, we face a fundamental tension. On one hand, we want the incredible reasoning and orchestration power of an LLM. On the other hand, we have strict, non-negotiable requirements around data privacy, specifically Personally Identifiable Information (PII), and stringent database security."
*   **Speaker:** "If we redact all PII, the LLM can't search for specific customer records. If we allow the LLM to write SQL dynamically, we open ourselves up to injection risks. The goal of dBank was to solve this tension—to build an agentic AI that is both incredibly capable and completely secure."

---

## Part 2: Architecture Deep Dive (15 Minutes)

**[Slide 3: High-Level Component Overview]**
*   **Speaker:** "Let's look at the architecture. The system is containerized via Docker and broken into distinct, isolated layers."
*   *Walk through the layers:*
    *   **Frontend:** Next.js handling the user experience.
    *   **Backend:** FastAPI acting as the orchestration brain.
    *   **Database:** A unified PostgreSQL instance that handles both our structured data and acts as our Vector Store via the `pgvector` extension.
    *   **Data Pipeline:** We use `dbt` (data build tool) to transform raw data into a clean Star Schema optimized for LLM querying.

**[Slide 4: Innovation 1 - Reversible PII Masking]**
*   **Speaker:** "To address the privacy challenge, I implemented a Reversible PII Masking strategy using Microsoft Presidio. This is perhaps the most critical part of the system."
*   *Explain the flow:*
    *   "When a user asks, 'Find the ticket for John Doe,' the backend intercepts this before the LLM sees it."
    *   "We mask 'John Doe' to a token like `<PERSON_1>` and store the mapping in temporary memory."
    *   "The LLM reasons over the query and says, 'I need to run a SQL query for `<PERSON_1>`'."
    *   "Before executing the SQL, the backend unmasks the token, runs the secure query against the real DB, re-masks the result, and feeds it back to the LLM."
    *   **Impact:** "The LLM never sees raw PII, mitigating data leakage, but still retains full functional capacity to execute exact-match searches."

**[Slide 5: Innovation 2 - Defense in Depth & Agentic Tools]**
*   **Speaker:** "For the LLM to interact with our systems, we utilize the Model Context Protocol (MCP) paradigm. We give the LLM specific, typed tools: `sql.query`, `kb.search`, and `kpi.top_root_causes`."
*   "But how do we make dynamic SQL secure? We use a Defense in Depth strategy:"
    1.  **Least Privilege:** The application runs as `app_user`, which only has read-only access to specific schemas.
    2.  **Parameterization:** We strictly use SQLAlchemy with bound parameters. The LLM cannot inject malicious syntax.
    3.  **Strict Validation:** Pydantic models validate every tool request before execution.

---

## Part 3: Live Demo (15 Minutes)

*   **Speaker:** "I'd like to shift from the architecture to showing you the system in action."
*   *Transition to the local environment (ensure Docker is running).*

**Demo Step 1: The RAG Capabilities**
*   *Action:* Type "What is the standard SLA for urgent network outages?" in the UI.
*   *Narration:* "Here, we are querying the unstructured Knowledge Base. The backend embeds the query and searches pgvector. Notice in the tool logs that it successfully called `kb.search`."

**Demo Step 2: The SQL & Orchestration Capabilities**
*   *Action:* Type "Show me the total number of critical tickets reported yesterday."
*   *Narration:* "Now we are asking a quantitative question. The LLM recognizes it needs structured data, formulates a query, and uses the `sql.query` tool. You can see the exact parameterized SQL it executed in the tool logs."

**Demo Step 3: Complex Multi-Tool Reasoning & PII Masking**
*   *Action:* Type "Find the most recent ticket for customer Acme Corp. What was the issue, and what does our internal policy say about handling that type of issue?"
*   *Narration:* "This is where the magic happens. The system first masks 'Acme Corp'. It runs a SQL query to find their ticket. It sees the issue was, for example, a 'Login Failure'. It then autonomously decides to run a *second* tool—a `kb.search` for 'Login Failure policy'—synthesizes both the DB row and the markdown document, and provides a cohesive answer."

---

## Part 4: Future Roadmap & Technical Trade-offs (10 Minutes)

**[Slide 6: Trade-offs & Future Scalability]**
*   **Speaker:** "To wrap up, I want to discuss a few technical decisions and how this scales."
*   **PostgreSQL + pgvector vs. Dedicated Vector DB (Pinecone):** "I chose pgvector to reduce operational complexity and infrastructure costs. For a corporate banking prototype, having transactional data and embeddings in one ACID-compliant database simplifies the architecture. At immense scale (billions of vectors), we might migrate to Pinecone, but pgvector with HNSW indexes easily handles millions of rows."
*   **The LLM Choice:** "We are using `gemma-4-31b-it`. It provides excellent reasoning for agentic workflows. However, in a true production banking environment, we would likely deploy a locally hosted, fine-tuned open-weight model (like Llama 3) to guarantee 100% data residency, entirely bypassing external APIs."
*   **Scalability:** "The stateless nature of the FastAPI backend allows us to horizontally scale the API layer easily behind a load balancer. The Next.js frontend is heavily optimized via standalone builds."

**[Final Slide: Q&A]**
*   **Speaker:** "Thank you for your time. I'd be happy to answer any questions about the architecture, the PII implementation, or the code."