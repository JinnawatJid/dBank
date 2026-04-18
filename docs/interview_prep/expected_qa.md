# Expected CTO Q&A Preparation

This document anticipates tough, high-level questions a CTO or technical panel might ask regarding the dBank architecture, specifically focusing on security, scalability, and technical decision-making.

---

### 1. Security & Data Privacy

**Q: "You mentioned Reversible PII Masking. What happens if the Presidio model fails to detect a custom entity? Doesn't that mean PII leaks to the external LLM?"**
*   **A:** "That is a valid risk. Presidio uses a combination of NER (Named Entity Recognition) and regex patterns. To mitigate leakage, I implemented custom recognizers explicitly for our domain, such as `BANK_ACCOUNT`. However, defense-in-depth is critical here. If a leak occurs, our secondary defense is that we never send the *entire* raw database row to the LLM. The SQL tools only return the specific columns requested. Furthermore, in a true production banking environment, the ultimate mitigation for this edge case is hosting the LLM internally (e.g., a locally hosted Llama 3 model) so that even if masking fails, the data never leaves the corporate VPC."

**Q: "Allowing an LLM to generate dynamic SQL terrifies me. How do you guarantee the LLM won't drop our tables or pull every user's data?"**
*   **A:** "I completely agree, which is why the system relies on strict infrastructure-level constraints, not just prompt engineering.
    1. The connection used by the MCP tool uses the `app_user` PostgreSQL role. This role is strictly `GRANT SELECT` only. It physically cannot execute `DROP`, `INSERT`, or `UPDATE`.
    2. We don't expose the raw schemas. The `app_user` only has access to the `marts` schema, which contains aggregated and pre-cleaned data via dbt.
    3. We use SQLAlchemy's `text()` with parameterized inputs, so SQL injection via tool arguments is neutralized."

---

### 2. Architecture & Tooling

**Q: "Why did you choose pgvector instead of a purpose-built vector database like Pinecone, Milvus, or Weaviate?"**
*   **A:** "For this architecture, introducing a separate vector database adds network latency, operational overhead, and data synchronization complexity (keeping relational state and vector state aligned). PostgreSQL is already an enterprise standard. `pgvector` allows us to leverage ACID compliance, existing backup strategies, and RBAC policies for both our relational data and embeddings. If we eventually hit tens of millions of dense vectors and query latency spikes, we can utilize HNSW indexes in pgvector, and only move to a dedicated solution if that ceiling is breached."

**Q: "Explain the role of dbt in this stack. Why not just write raw SQL views?"**
*   **A:** "dbt provides software engineering best practices to data transformations. Instead of opaque SQL views, dbt gives us version control, automated data testing (like checking for nulls or referential integrity), and automatic lineage documentation. More importantly, it transforms our raw, complex operational data into a clean Star Schema (fact and dimension tables). This drastically simplifies the schema the LLM has to understand, reducing hallucinations and improving the accuracy of the generated SQL."

**Q: "I see you used Next.js for the frontend. Did you consider a simpler React SPA? Why Next.js?"**
*   **A:** "Next.js was chosen for its robust App Router and built-in optimization. By using Next.js, we can leverage server-side rendering (SSR) or React Server Components to keep sensitive logic or initial API calls off the client-side bundle. Furthermore, the `standalone` output mode creates a highly optimized Docker container, which is critical for efficient deployments. It aligns perfectly with modern enterprise frontend standards."

---

### 3. LLM Limitations & Edge Cases

**Q: "What happens when the LLM hallucinates a SQL table or column that doesn't exist?"**
*   **A:** "This is handled gracefully by our backend error handling. When the LLM calls the `sql.query` tool with a bad query, the SQLAlchemy execution will throw an exception (e.g., `ProgrammingError`). Our backend catches this, executes a `session.rollback()` to keep the database connection healthy, and returns a formatted error string *back to the LLM* as the tool result. The LLM sees 'Error: Column X does not exist' and can autonomously retry and self-correct its query in the next turn."

**Q: "How do you handle rate limits or API failures from Google AI Studio?"**
*   **A:** "The backend implements robust error handling around external API calls. I'm using `try/except` blocks to specifically catch `429 Quota Exceeded` and `500 Internal Error` exceptions. Instead of crashing the FastAPI server, it gracefully returns a standardized JSON error response to the frontend, which displays a friendly 'System busy, please try again' message to the user."