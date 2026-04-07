# Engineering Post-Mortem

This document serves as an engineering log detailing the critical issues, integration challenges, and architectural fixes encountered during the development of the **dBank Deep Insights Copilot**.

## 1. Vector Dimension Mismatch Trap

**Issue:** An error occurred during the Knowledge Base embedding insertion: `expected 768 dimensions, not 3072`.
**Root Cause:**
- The initial development utilized Google's `models/text-embedding-004`, which outputs 768-dimensional vectors. However, this legacy model was deprecated mid-development (returning `404 Not Found`).
- When upgrading to the modern industry-standard `models/gemini-embedding-001`, the generated vector dimensionality increased to 3072.
- The PostgreSQL `pgvector` table (initialized via `02-init-kb-schema.sh`) was statically bound to `embedding vector(768)`.
**Resolution:**
- Updated the SQL schema to `vector(3072)`.
- Synchronized the application logic's CI/CD sandbox fallback generator to output `3072` random dimensions if the API key is missing.
- Refreshed the Docker PostgreSQL volume (`docker compose down -v`) to safely wipe the schema constraint and re-initialize the environment.

## 2. Protobuf `MapComposite` Output Serialization Bug

**Issue:** The FastAPI `/ask` endpoint crashed with `TypeError: Object of type MapComposite is not JSON serializable` generating a `500 Internal Server Error`.
**Root Cause:**
- When the LLM utilized `sql.query` and passed parameterized dictionary arguments (e.g., `params={"customer_name": "John"}`), the `google-generativeai` SDK natively output nested Protobuf structures.
- Casting `dict(function_call.args)` successfully converted the top-level structure but left the nested dictionary as a Protobuf `MapComposite` class. The `audit.py` logger subsequently crashed when attempting to execute `json.dumps()`.
**Resolution:**
- Implemented a custom recursive unrolling function (`_unroll_proto`) inside the fast-path of `routes.py` tool parsing. This ensures nested Protobuf mapping objects are fully coerced into native Python dictionaries safely before hitting the masking engine and the audit log.

## 3. Google API 500 Internal Error (Prompt Injection Limitation)

**Issue:** The Google Generative AI API threw a non-descriptive `500 Internal error encountered` immediately upon receiving the user message.
**Root Cause:**
- Attempting to suppress LLM "thinking-out-loud" hallucinations (where it leaks document filenames to the user) by injecting strict negative constraints directly into the current execution loop (`"CRITICAL RULES: Never explicitly mention tool names..."`).
- This direct prompt injection likely caused an internal parsing crash or triggered an automated Google constraint guardrail within the Vertex function-calling engine, leading to an upstream crash.
**Resolution:**
- Reverted the hardcoded negative string injection to a pure `f"User: {masked_query}"` format. Relied on pure `system_instruction` injection at model initialization, significantly improving API stability.

## 4. Docker Compose Caching Hell (Environment Drift)

**Issue:** Development updates to `backend/mcp_tools.py` resolving 404 errors were not reflecting during runtime, heavily prolonging the debugging phase.
**Root Cause:**
- Using `docker compose up -d` relies on the Docker image's cached state. Without passing the `--build` flag or explicitly establishing volume mounts, the `backend` container remained locked onto older script iterations.
**Resolution:**
- Converted container paths into hot-reload execution by adding host-to-container volume mappings (`- ./backend:/app/backend` and `- ./scripts:/app/scripts`) within the `docker-compose.yml`. This adhered to the industry standard of bypassing static image rebuilding during iterative development.

## 5. Nested PII Unmasking Bug (Silent Query Failure)

**Issue:** SQL queries using parameterized arguments (e.g., `params={"full_name": "Jessica Graham"}`) always returned empty results, even when the customer existed in the database.
**Root Cause:**
- The PII Masker correctly masked the customer name in the user query (e.g., `"Jessica Graham"` → `<PERSON_xxx>`).
- The original `unmask_text` loop only iterated over the **top-level keys** of `tool_args`. When the LLM returned nested structures (e.g., `{'template': '...', 'params': {'full_name': '<PERSON_xxx>'}}`), the inner `params` dictionary was not recursively traversed.
- As a result, the literal placeholder token `<PERSON_xxx>` was sent to PostgreSQL as the search value, which obviously matched nothing.
**Resolution:**
- Replaced the shallow loop with a recursive `_recursive_unmask()` function in `backend/api/routes.py` that deep-traverses `dict`, `list`, and `str` types, ensuring all PII tokens are resolved before tool execution regardless of nesting depth.

## 6. Orchestration Turn Exhaustion (Max Turns Too Conservative)

**Issue:** Queries requiring schema exploration followed by a query returned `"I'm sorry, I couldn't find a complete answer after several attempts."` even when the SQL tool had successfully retrieved the data.
**Root Cause:**
- The orchestration loop was capped at `max_turns = 5`.
- A realistic LLM reasoning path for an unknown schema requires: (1) list tables, (2) inspect column names of target table, (3) optionally inspect staging table, (4) execute the query, (5) generate the final text response.
- This is a minimum of 5 sequential tool calls + 1 final generation turn = 6 turns. The cap of 5 caused the loop to exit immediately after receiving successful tool results, before the LLM could generate the answer.
**Resolution:**
- Increased `max_turns` to `10` in `backend/api/routes.py`, with a comment explaining the turn budget breakdown (`schema exploration (2-3) + query retry (1-2) + final answer (1)`).

## 7. Defense-in-Depth: Output PII Guardrail

**Issue:** The system successfully retrieved and unmasked customer PII (email, phone) and returned it directly in the LLM response with no final verification layer.
**Root Cause:**
- The existing PII Masking pipeline was designed to protect data flowing *into* the LLM, not data flowing *out of* it.
- After `unmask_text()` restored real values from the PII mapping, there was no mechanism to verify that the final response was safe to return to the caller.
**Resolution:**
- Added a dedicated `scan_for_pii()` method to `backend/core/security.py` following the **Single Responsibility Principle** — it performs read-only PII detection without mutating data, and **fails CLOSED** (treats scanner errors as PII detected).
- Integrated a final Output PII Guardrail in `backend/api/routes.py` that invokes `scan_for_pii()` on the final, unmasked response before it is returned.
- If PII is detected, the system fires an `OUTPUT_PII_BLOCKED` audit event, logs a security warning, and returns a safe generic message directing users to the CRM portal instead.
- This follows the **Defense-in-Depth** security principle: multiple independent layers of protection ensure that a failure in any one layer does not expose sensitive data.
