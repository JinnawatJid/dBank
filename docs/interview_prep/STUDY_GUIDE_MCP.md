# MCP (Model Context Protocol): Study Guide for NotebookLM

## What is MCP?
MCP stands for **Model Context Protocol**. It is an open standard introduced by Anthropic (creators of Claude) designed to standardize how AI models connect to external data sources and tools.

Think of it like **"USB-C for AI."** Before USB-C, every phone had a different charger. Before MCP, every AI developer had to write custom, messy code to let an LLM talk to a specific database, a specific API, or a specific file system. MCP provides a universal, standardized way to say: "Here is a list of tools you can use, here is how you use them, and here is the data they return."

## The Core Problem MCP Solves
LLMs are essentially "brains in a jar." They can think and reason, but they have no hands to do things (like run a SQL query) and no eyes to see live data (like checking a live stock price).
To give them hands and eyes, developers use **Tool Calling** (or Function Calling). However, managing tool calling securely and consistently across different LLMs and different environments is extremely difficult. MCP standardizes this architecture.

## How MCP Works (The Client-Server Model)
MCP operates on a simple Client-Server architecture:
1.  **The MCP Server:** This is a lightweight program running on your backend. It connects directly to your databases, APIs, or local files. It exposes a standardized list of "Tools" (e.g., `sql.query`, `github.read_repo`).
2.  **The MCP Client:** This is the AI application (like our FastAPI backend interacting with Gemini/Google AI).
3.  **The Interaction:**
    *   The Client asks the Server: "What tools do you have?"
    *   The Server replies with a structured list of tools and the strict parameters required to use them (usually defined by JSON Schema).
    *   The LLM decides it needs to use a tool. The Client sends a request to the Server: "Run `sql.query` with these parameters."
    *   The Server runs the code securely, and returns the result to the Client.

## Why MCP is Critical for the dBank Project (Security & Guardrails)
In the dBank assignment, using MCP tools for SQL and KPI queries isn't just about standardization; it's about **Enterprise Security**.

*   **Pydantic Validation (Strict Typing):** In our MCP implementation, every tool requires a `Pydantic` schema. If the LLM hallucinates and tries to pass a string where an integer is required, the Pydantic validator catches it *before* it hits the database.
*   **Preventing SQL Injection:** By forcing the LLM to use an MCP tool named `sql.query`, we prevent the LLM from executing raw text against the database. The tool is programmed to accept a SQL template and a separate JSON object of variables. The backend then safely binds these variables using SQLAlchemy parameterized queries.
*   **Separation of Concerns:** The LLM does the reasoning. The MCP Server does the execution. The LLM never has the actual database password. It only has permission to say "Please trigger this specific tool."

## Key Concepts to Remember for NotebookLM
*   **Tool Calling / Function Calling:** The ability of an LLM to output a structured JSON command telling an external system to run a specific script.
*   **JSON Schema:** The language MCP uses to describe exactly what inputs a tool requires.
*   **Agentic AI:** When an AI can use tools autonomously in a loop (think, act, observe) to solve complex problems. MCP is the foundational protocol that enables reliable Agentic AI.