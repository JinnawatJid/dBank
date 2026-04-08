# AI Guardrails: Study Guide for NotebookLM

## What are AI Guardrails?
In enterprise AI, **Guardrails** are strict boundaries placed around a Large Language Model (LLM) to ensure it behaves safely, predictably, and legally. LLMs are naturally unpredictable and eager to please. Without guardrails, a simple prompt like "Show me everyone's password" or "Delete the customer table" could cause catastrophic damage if the AI is connected to a live database.

In the dBank project, the assignment explicitly required four mandatory guardrails:
1.  **Read-only DB Access**
2.  **PII (Sensitive Data) Must be Masked**
3.  **Parameterized Tool Calls**
4.  **Logging**

Let's break down how to study and understand each one.

---

## 1. Read-Only DB Access (Zero Trust Architecture)
**The Concept:** Never trust the AI. Even if you tell the AI "Do not delete data," a clever user can use "Prompt Injection" to trick the AI into running a `DROP TABLE` command.

**The Implementation:**
We enforce security at the Database Engine level, not the Prompt level.
*   We create a specific database user role (e.g., `dbank_app`).
*   We grant this role `SELECT` (read) permissions *only*. We explicitly deny `INSERT`, `UPDATE`, `DELETE`, and `DROP` permissions.
*   We scope this access further by only allowing it to read from the `marts` schema (cleaned, transformed data), completely blocking access to the `raw` schema.
*   **Result:** Even if the AI generates malicious SQL, the PostgreSQL database will reject it with a "Permission Denied" error.

---

## 2. PII (Sensitive Data) Must be Masked
**The Concept:** PII stands for Personally Identifiable Information (Names, Phone Numbers, Emails, Bank Accounts). We cannot send raw PII to external APIs (like Google's Gemini) due to data privacy laws like GDPR or PDPA.

**The Implementation (Reversible Tokenization):**
We use a scanner (like Microsoft Presidio or Regex) to act as a middleman.
*   **Input Masking:** When a user types "What is John Doe's balance?", the scanner intercepts it. It maps "John Doe" to a token, e.g., `<PERSON_UUID_123>`. The LLM only sees "What is `<PERSON_UUID_123>`'s balance?".
*   **Execution Unmasking:** The LLM decides to use the `sql.query` tool to find the balance for `<PERSON_UUID_123>`. Before the backend runs the SQL against our private database, it looks up the UUID in memory and replaces it back with "John Doe".
*   **Output Guardrail:** Before the final answer is sent to the user's screen, a final scanner checks the output to ensure no accidental PII is leaking out of the database into the chat window.

---

## 3. Every Tool Call Must be Parameterized
**The Concept:** When executing SQL, combining a user's raw text directly into a SQL string is highly dangerous. It leads to **SQL Injection**, where a user types malicious SQL instead of a normal word, tricking the database into executing it.

**The Implementation:**
*   We forbid "String Concatenation" (e.g., `query = "SELECT * FROM users WHERE name = " + user_input`).
*   Instead, we force the LLM to provide a SQL Template and a separate JSON dictionary of Parameters via the MCP protocol.
*   We use **SQLAlchemy Parameterized Queries** (e.g., `text("SELECT * FROM users WHERE name = :name")` with `params={"name": user_input}`).
*   **Result:** The database engine strictly treats the `user_input` as literal data (a string), never as an executable SQL command, making SQL injection mathematically impossible.

---

## 4. Logging (Audit Trails)
**The Concept:** In banking, observability is mandatory. If an AI makes a mistake or a user tries to abuse the system, the security team needs a forensic trail to understand exactly what happened.

**The Implementation:**
*   We implement **Structured JSON Logging**. Instead of printing messy text to a console, every event is recorded as a neat JSON object containing standard keys (`timestamp`, `event_type`, `user_id`, `tool_name`, `execution_time`).
*   **What we log:**
    *   Every time an MCP tool is invoked (which tool, what parameters).
    *   Every time a prompt injection attack is blocked.
    *   Every time PII is detected and masked.
*   **Crucial Rule:** We ensure that the logger itself is "PII-aware." We never write unmasked PII into the log files, as log files are often stored in less secure environments (like CloudWatch or Elasticsearch) than the primary database.