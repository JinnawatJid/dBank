To: joey@data.co.th
Subject: Submission: Deep Insights Copilot - 5-Days Data Deep Lab Exam

Hi Joey,

Please find my submission for the "Deep Insights Copilot" project attached. [Insert GitHub Link or indicate Zipped Folder is attached]

Overall, the core architecture attempts to implement the requirements specified in the exam brief. Here is a summary of what has been built:

Completed Features & Alignments:
Data Layer: Implemented dbt transformations to model the raw synthetic data (Customers, Tickets, Logins, Products) into a star schema (marts) within PostgreSQL.
Knowledge Retrieval Layer: Markdown documents are chunked and stored in a pgvector database, and the kb.search MCP tool is implemented.
Core API & GenAI Orchestration: Built the FastAPI /ask endpoint to orchestrate LLM interactions and implemented Reversible PII Masking (via Microsoft Presidio) to ensure sensitive data is not sent to the LLM.
MCP Tools: Developed the required tools (sql.query, kb.search, kpi.top_root_causes) utilizing parameterized execution to prevent SQL injection.
DevOps: The stack is containerized using Docker Compose.

Known Issues & Architectural Reflections: While the foundation is there, the system is not fully stable. During testing, the LLM orchestration loop encounters several flaws (e.g., hitting the max turn limit, SQL schema hallucinations). I want to be completely transparent about the root causes of these issues, which stem from unforeseen challenges and poor time management on my end:

Embedding Model 404 Error: The kb.search tool frequently fails because I did not properly research Google's embedding models or verify API compatibility before implementation. I blindly used a model (models/text-embedding-004) that caused a 404 error, and rather than fixing the root cause, the system falls back to returning random vectors. This completely breaks the semantic search accuracy.
Environment Drift (Linux vs. Windows): I relied heavily on an AI Agent to help develop the system within a Linux Sandbox environment. When I transitioned to testing and running the system on my local Windows machine, I encountered severe environment compatibility issues that I had not anticipated, severely impacting my development timeline.
Sudden LLM Model Switch: Mid-development, I hit API rate limits with gemini-2.5-pro and made a hasty switch to gemma-4-31b-it. Because the response payloads and function-calling structures differ between the two models, my API parsing logic broke. Trying to hotfix this further consumed my time.
Time Management: Dealing with the environment drift and the sudden model switch left me without enough time to properly stabilize the LLM's SQL orchestration (which suffers from schema hallucination) and fix the embedding logic before the deadline.

Future Improvements / Lessons Learned: If I were to rebuild or continue this project, I would implement the following industry standards:

Thorough API Research: Verify model availability, rate limits, and payload structures via Postman or simple scripts before integrating them into the core backend.
Environment Standardization: Ensure Development, Testing, and Production environments are strictly aligned from Day 1, relying less on sandbox specificities and testing locally much earlier.
Context Injection: Inject the database schema (DDL) directly into the LLM's system prompt to cure the SQL schema hallucinations, rather than letting the LLM guess the table structures.
Graceful Degradation: Instead of generating "dummy vectors" when an API fails, the system must "Fail Fast" and explicitly inform the LLM that the Knowledge Base is currently unavailable.

This project was an incredible learning experience that exposed gaps in my deployment planning and API research. Thank you for the opportunity, and I look forward to your feedback.

Best regards,

[Your Name] [Your Contact Information]