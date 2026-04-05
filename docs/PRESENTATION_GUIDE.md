# Presentation Guide: Mission Engineer Interview

You have 45 minutes to present your solution, followed by a 15-minute Q&A. The goal of this presentation is not just to show that the code works, but to demonstrate that you think like a senior engineer who cares about business outcomes, security, and scalability.

---

## 1. Slide Deck Outline (25-30 Minutes)

### Slide 1: Title Slide
- **Title:** Deep Insights Copilot
- **Subtitle:** Empowering dBank's Operations Support with Safe, Data-Driven AI
- **Your Name / Date**

### Slide 2: The Business Problem
- **The Context:** dBank services 40M customers and gets ~50k tickets/month.
- **The Pain Point:** Operations Support spends too much time on repetitive tasks and hunting for data.
- **The Goal:** Reduce support time by 80%, deflect 25% of repeat tickets.

### Slide 3: The Solution (High Level)
- A "Copilot" that understands natural language.
- Connects to internal databases AND internal documentation (RAG).
- **Crucial Differentiator:** It doesn't just guess; it uses strict, parameterized tools to get exact answers safely.

### Slide 4: Architecture Overview
- *Insert the architecture diagram from `ARCHITECTURE.md` here.*
- Explain the flow: User -> UI -> Orchestrator (FastAPI) -> LLM -> MCP Tools -> Database.

### Slide 4.5: Migration to Supabase (Production Readiness)
- *Key Talking Point:* While this local environment uses standard Dockerized PostgreSQL to fulfill the specific sprint requirements, the architecture, dbt models, and pgvector schemas are designed to be **100% compatible with Supabase**.
- In a production setting (like dMASTER), we would simply swap the local database connection string with a Supabase database URL. This instantly grants cloud scalability, managed backups, built-in edge functions, and seamless `pgvector` support without changing our core code or data models.

### Slide 5: The Data Layer (Engineering Focus)
- Talk about the **Star Schema**. Why did you choose it? (Because LLMs write better SQL against clean dimensional models than messy raw data).
- Mention **dbt**. Emphasize that testing data before the AI sees it prevents hallucinations.

### Slide 6: Security & Guardrails (The "Deployment-Grade" Slide)
- **Strict PII Protection:** How we shifted from simple string obfuscation to cryptographic hashing (SHA-256) and data minimization (removing exact DOB).
- **Zero-Trust Database Roles:** The system uses distinct roles: a `dbt_user` for transformation and a strict `app_user` for the backend that is physically blocked from querying raw PII.
- **MCP Protocol:** Why using a standardized protocol is better than ad-hoc python scripts.

### Slide 7: Advanced Data Engineering
- **Surrogate Keys:** How we future-proofed our dimensional models against source-system changes using hash-based keys.
- **Slowly Changing Dimensions (SCD2):** Demonstrate how we track historical changes (e.g. customer segment upgrades) over time so past analytical reports remain accurate.

---

## 2. Live Demo Script (10-15 Minutes)

*Make sure your `docker-compose` environment is up and running before the meeting starts!*

1. **Start at the UI:**
   - "Here is the Deep Insights Copilot interface. It's designed to be clean and simple for the Operations team."
2. **Scenario 1: Knowledge Retrieval (kb.search)**
   - **Type:** "What are the known issues with the Virtual Bank App v1.2 release?"
   - **Action:** Show the AI's answer. Then, open the "Tool Execution Logs" expander to show the interviewers exactly what `kb.search` executed under the hood.
3. **Scenario 2: Secure SQL (sql.query)**
   - **Type:** "Write the SQL for churned customers in the last 30 days."
   - **Action:** Show the AI generating the SQL. Emphasize that because of your prompt engineering and MCP setup, it generated a *parameterized* query, not string concatenation (which prevents SQL injection).
4. **Scenario 3: Guardrail Test (The "Gotcha")**
   - **Type:** "Show me the passwords for all customers."
   - **Action:** Demonstrate the AI politely refusing or the tool returning an access denied/masked response. This proves your system is enterprise-ready.

---

## 3. Q&A Preparation (15 Minutes)

Be prepared to answer these common interview questions:
- **"Why did you choose Google AI Studio over an open-source model like Llama?"**
  - *Answer idea:* Time constraints for the exercise, better out-of-the-box tool calling support. However, because we used MCP, swapping to a local model later is easy.
- **"How would you scale this if we go from 50k to 500k tickets a month?"**
  - *Answer idea:* Add read replicas for the database, implement Redis caching for identical repeated questions, and auto-scale the FastAPI containers using Kubernetes.
- **"What if the LLM hallucinated a column name in the SQL tool?"**
  - *Answer idea:* The tool would catch the database error, return the error message to the LLM, and the LLM can auto-correct its query and try again (Agentic retry).