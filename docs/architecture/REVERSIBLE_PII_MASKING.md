# Reversible PII Masking Architecture

To maintain the highest level of data privacy in corporate banking systems, while simultaneously allowing complex orchestration via Large Language Models (LLMs), Deep Insights Copilot employs a **Tokenization and Reversible PII Masking Strategy**.

## The Challenge
If we completely strip PII from a user query (e.g., replacing "John Doe" with `[PERSON]`), the LLM will lack the specific identifiers needed to instruct database search tools. An LLM cannot execute `SELECT * FROM users WHERE name = '[PERSON]'` and expect a valid database result.

## The Solution: Tokenization
We intercept the user query before it reaches the LLM and pass it through a custom configuration of Microsoft Presidio.

1. **Detection**: Presidio detects entities, including both standard entities (e.g., `PERSON`, `EMAIL`) and custom banking entities (e.g., `BANK_ACCOUNT`, `CREDIT_CARD`).
2. **Token Generation**: Instead of permanent redaction, the system replaces these entities with unique, sequential placeholders (e.g., `<PERSON_1>`, `<BANK_ACCOUNT_1>`).
3. **In-Memory Mapping**: The system stores a temporary dictionary mapping these placeholders back to the original values. This mapping lives only for the duration of the API request lifecycle.

```json
// Original text: "Find the ticket for John Doe."
// Masked text given to LLM: "Find the ticket for <PERSON_1>."
// Memory Mapping: {"<PERSON_1>": "John Doe"}
```

## End-to-End Orchestration Flow
1. **User Input Phase**: The user submits a query. The backend applies Reversible Masking. The masked query is sent to the LLM.
2. **Tool Execution Phase**: If the LLM requests a tool (e.g., executing a SQL query), it will naturally use the placeholder (e.g., `name = '<PERSON_1>'`). Before the application runs the actual SQL query against the database, the backend intercepts the tool arguments and **unmasks** them using the dictionary mapping.
3. **Tool Result Phase**: The database returns real PII. The backend applies the mask *again* to the database results before feeding them back into the LLM context.
4. **Final Answer Phase**: The LLM generates its final natural language answer using placeholders. Before this answer is returned to the client, the backend **unmasks** the response.

## Security Posture
By using this architecture:
* The LLM *never* sees raw PII, mitigating data leakage to external models.
* The system remains highly functional, capable of performing exact-match database queries.
* Comprehensive **Audit Logging** records only the masked texts, ensuring regulatory compliance.