# Gamma AI Presentation Prompt

To quickly generate a beautiful, professional presentation using **Gamma.app**, use the "Text to Presentation" feature.

**Instructions:**
1. Go to [Gamma.app](https://gamma.app) and create a new presentation.
2. Select **"Generate"** and then **"Text to Presentation"** (or "Paste in Text").
3. Set the desired number of cards/slides to **8**.
4. Choose a professional, dark-mode theme (like "Midnight" or "Cyber") to match the technical, enterprise feel of dBank.
5. Copy and paste the entire prompt box below into Gamma.

---

### Copy this text into Gamma AI:

```text
Please create a highly professional, enterprise-grade technical presentation for a CTO audience. Use a dark, modern aesthetic. The presentation should have 8 slides based exactly on the outline below. Do not add filler text; keep it concise and technical.

**Slide 1: Title**
Title: dBank: Enterprise Deep Insights Copilot
Subtitle: Secure, Agentic Data Exploration for Corporate Banking
Presenter: Jinnawat Jidsanoa - Mission Engineer Candidate

**Slide 2: The Friction of Enterprise LLM Deployment**
- The Promise: LLMs offer unparalleled orchestration and natural language data exploration.
- The Reality: Highly regulated environments (Banking) have strict constraints on Data Privacy (PII) and Database Security.
- The Tension: If we redact PII, the LLM can't search accurately. If we allow dynamic SQL, we risk systemic breaches via injection.
- Visual: Include a visual representing a balance scale between AI Capabilities and Enterprise Security.

**Slide 3: The dBank Solution Architecture**
- Concept: Containerized, Secure-by-Design
- Frontend: Next.js Chat UI (Modern, SSR-optimized)
- Backend: FastAPI Orchestrator (High-performance python)
- Intelligence: Google Gemma via Model Context Protocol (MCP)
- Data Store: PostgreSQL + pgvector + dbt (Single ACID-compliant database handling relational data and vectors)
- Visual: Include a conceptual architecture diagram connecting UI -> Backend -> AI & Data Store.

**Slide 4: Innovation 1 - Reversible PII Masking**
- Concept: Solving the Privacy Paradigm via Tokenization
- Interception: Microsoft Presidio detects custom banking entities (e.g., BANK_ACCOUNT) before reaching the LLM.
- Tokenization: PII is replaced with UUID placeholders (e.g., <PERSON_1>).
- Reversible Mapping: Ephemeral in-memory dictionary maps tokens back to reality during backend tool execution.
- Result: The external LLM never processes raw PII, while the system retains exact-match query capabilities.

**Slide 5: Innovation 2 - Defense in Depth SQL Execution**
- Concept: Agentic Capabilities Without Compromise
- Least Privilege: MCP server uses a restricted `app_user` role (Read-Only / SELECT).
- Schema Segregation: Access is limited to the dbt-transformed `marts` schema—never raw data.
- Parameterization: SQLAlchemy strictly binds parameters, neutralizing LLM-generated SQL injection vectors.
- Input Guardrails: Pydantic models validate all tool requests prior to execution.
- Visual: A security or shield icon representing layers of defense.

**Slide 6: Live System Demonstration**
- Concept: dBank in Action
- Scenario 1 (Unstructured RAG): Querying internal policies via pgvector similarity search.
- Scenario 2 (Structured SQL): Dynamically querying aggregated ticket volumes.
- Scenario 3 (Complex Orchestration): Combining SQL data retrieval with PII masking and Knowledge Base synthesis.
- Layout: Leave a large blank space or placeholder on this slide for me to embed a live screen share or video.

**Slide 7: Architectural Decisions & The Roadmap**
- Concept: Technical Trade-offs
- PostgreSQL/pgvector vs. Dedicated Vector DB: Chosen for ACID compliance and reduced operational overhead. Pinecone considered for massive scale (>100M vectors).
- dbt vs. Raw SQL Views: Enforces software engineering CI practices on the data pipeline, resulting in cleaner LLM context.
- Cloud LLM vs. Local Model: Currently utilizing Gemma; production banking roadmap entails a locally-hosted Llama 3 to guarantee absolute data residency.

**Slide 8: Questions & Discussion**
- Title: Q&A
- Thank you for your time.
```