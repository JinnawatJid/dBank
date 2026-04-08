# dData Mission Engineer Interview: Anticipated Q&A

This document contains expected questions from a CTO or technical panel based on the `dBank` Deep Insights Copilot architecture, along with strategic answers.

---

### Category 1: Architecture & Data Engineering

**Q1: ทำไมระบบถึงเลือกออกแบบ Data Pipeline เป็นแบบ ELT (Extract, Load, Transform) แทนที่จะเป็น ETL แบบดั้งเดิมล่ะ?**
**Answer:** "เหตุผลหลักคือเรื่องของ Performance คอขวด และความยืดหยุ่นครับ
ถ้าเราใช้ ETL แบบเดิมที่เอาข้อมูลไป Transform ใน Python ก่อน สมมติในสเกลจริงของ Virtual Bank อย่าง dBank ที่อาจจะมีข้อมูล Transaction หรือ Ticket ถึง 10-100 ล้านเรคคอร์ด การใช้ Python อ่านไฟล์ CSV ทั้งหมดมาพักไว้ใน RAM เพื่อทำ Transform จะทำให้เกิดปัญหาคอขวด ประมวลผลช้า หรือเซิร์ฟเวอร์ค้าง (Out of Memory) ไปเลยครับ

ดังนั้นเราจึงแก้ปัญหานี้ด้วยท่า **ELT** โดยเปลี่ยนให้ Python ทำหน้าที่แค่ Extract แล้วโหลด (Load) ข้อมูลดิบทั้งหมดโยนโครมลงไปใน PostgreSQL ที่ schema `raw` ทันทีครับ เพราะ Database อย่าง PostgreSQL ถูกสร้างมาเพื่อจัดการกับข้อมูลมหาศาลอยู่แล้ว เราจึงยืมพลังประมวลผล (Compute Power) ของมันมาทำ Transform ด้วย dbt แทน

และอีกข้อดีที่สำคัญมากคือ **ความยืดหยุ่น** ครับ เพราะเรามีข้อมูลดิบต้นฉบับเก็บไว้ที่ schema `raw` เสมอ ในอนาคตถ้า Business เปลี่ยน Requirement เช่น อยากเปลี่ยนสูตรคำนวณ KPI ใหม่ เราก็สามารถไปแก้ Logic ใน dbt แล้วรันดึงข้อมูลจาก `raw` มาคำนวณใหม่ได้ทันที โดยไม่ต้องกลับไปเริ่มอ่านไฟล์ CSV ใหม่ตั้งแต่ต้นครับ"

**Q2: ถ้าไปดูโค้ดในชั้น Staging (เช่น `stg_customers.sql`) ดูเหมือนจะแค่ SELECT คอลัมน์ออกมาเฉยๆ ไม่เห็นมีการทำ Cleansing อะไรซับซ้อนเลย ทำไมถึงบอกว่าทำ Cleansing?**
**Answer:** "ในโปรเจกต์นี้ การทำ Cleansing พื้นฐานของเราคือการทำ **Schema Enforcement** และ **Column Selection** ครับ
แทนที่เราจะใช้คำสั่ง `SELECT *` ดึงข้อมูลทั้งหมดจากตารางดิบ (raw) ซึ่งมีความเสี่ยงที่คอลัมน์ขยะหรือข้อมูลแปลกปลอมที่เพิ่มเข้ามาในอนาคตจะหลุดเข้ามาในระบบ เราเลือกที่จะระบุชื่อคอลัมน์แบบเจาะจง (Explicit Declaration) เพื่อกรองและดึงเฉพาะข้อมูลที่มี Business Value จริงๆ เท่านั้นไปใช้ต่อครับ นี่คือการคลีนข้อมูลขยะชั้นแรกที่ได้ผลและปลอดภัยที่สุดครับ"

**Q3: Why did you choose dbt for this project instead of just writing SQL scripts or relying on the backend to transform data?**
**Answer:** "In a corporate banking context, data integrity and modularity are paramount. I chose dbt because it treats SQL like software. It allows us to build staging and mart layers (a Star Schema) modularly, ensures idempotency, and most importantly, allows us to write built-in data tests. We need to guarantee the LLM is querying clean, validated data, not raw, messy logs."

**Q4: You used PostgreSQL with `pgvector`. Why not a dedicated vector database like Pinecone or Weaviate?**
**Answer:** "For an MVP and often for early-stage production, minimizing infrastructure complexity is key. PostgreSQL is incredibly robust. By using the `pgvector` extension, we can keep our relational business data (like customer tables) and our vector embeddings in the exact same ecosystem. This simplifies deployment, backups, and access control. If vector scale becomes an issue (e.g., millions of dense embeddings), migrating to a specialized DB is easy, but starting with Postgres is the leanest, most reliable approach."

**Q5: How do you handle schema evolution? If the database schema changes, how does the LLM know?**
**Answer:** "The MCP server is designed to allow the LLM to 'explore' the schema. Because it can execute read-only queries, a complex reasoning loop allows it to query `information_schema` to understand available tables and columns before writing its final query. However, for production, I would explicitly inject a schema summary (a data dictionary) into the LLM's system prompt or context window upon initialization to reduce token usage and API calls."

---

### Category 2: Security & Guardrails

**Q4: A massive concern with LLMs writing SQL is SQL injection. How did you definitively prevent this?**
**Answer:** "I implemented a strict 'Defense-in-Depth' strategy. First, the LLM isn't writing raw executable strings. It's using an MCP tool (`sql.query`) that forces it to provide a SQL template and a separate JSON object of parameters. On the backend, we use SQLAlchemy parameterized queries (`text()`). The database engine treats the parameters strictly as data, making traditional SQL injection impossible. Second, the database user executing the query only has `SELECT` privileges on specific schemas."

**Q5: Explain your PII masking strategy. How do you ensure sensitive customer data doesn't leak to Google AI?**
**Answer:** "We use a reversible tokenization approach. Before any user prompt hits the LLM, a scanner (using regex or tools like Microsoft Presidio) identifies entities like names or account numbers and replaces them with a UUID-based token (e.g., `<PERSON_123>`). The LLM only sees the token. When the LLM calls a tool using that token, our backend intercepts it, recursively deep-traverses the payload to unmask the real value, runs the query securely locally, and then re-masks any new PII in the results before returning it to the LLM."

**Q6: I saw in your Post-Mortem you mentioned an 'Output PII Guardrail'. Why was the input masking not enough?**
**Answer:** "Input masking protects data going *to* the LLM. However, if an MCP tool executes a query like `SELECT * FROM customers`, the database returns real PII to the backend. If that data is accidentally passed back to the LLM without masking, or if the final response to the user contains unmasked PII that shouldn't be there, we have a breach. The Output Guardrail is a final, independent scanner that runs right before the HTTP response is sent to the UI. If it detects PII, it fails closed, preventing a leak. It's a necessary redundant layer."

---

### Category 3: AI/LLM Integration

**Q7: Why build a custom Model Context Protocol (MCP) implementation instead of using LangChain or LlamaIndex?**
**Answer:** "Frameworks like LangChain are excellent, but they can be highly opinionated and sometimes obscure the underlying execution flow, which makes debugging difficult (the 'black box' problem). For a banking MVP where security and exact tool execution control are critical, I wanted explicit control over the orchestration loop, Pydantic validation, and the `try/except/rollback` mechanics. Building a lean MCP allowed me to enforce strict security boundaries without framework bloat."

**Q8: You mentioned the Google API throwing a 500 error due to Prompt Injection constraints. Can you elaborate?**
**Answer:** "Yes, initially, I tried to inject negative constraints directly into the conversational turn (e.g., passing 'Never do X' alongside the user's message). This often conflicts with the internal safety classifiers of the Vertex/Gemini function-calling engine, leading to unpredictable 500 errors. I learned that it's much more stable to define the persona and strict rules entirely within the `system_instruction` at the model initialization phase, and keep the user's conversational turns clean."

**Q9: How do you handle hallucinated tool arguments?**
**Answer:** "This is where Pydantic is critical. Every MCP tool has a strict Pydantic schema. If the LLM tries to pass a string where an integer is required, or invents a parameter that doesn't exist, Pydantic throws a `ValidationError`. Our backend catches this exception and returns a formatted error string *back to the LLM* (e.g., 'Error: Invalid parameter. You must provide X.'). The orchestration loop then gives the LLM a chance to self-correct in the next turn."

---

### Category 4: DevOps & Future Scale

**Q10: Your MVP runs locally on Docker Compose. How would you deploy this to AWS or GCP in a production environment?**
**Answer:**
*   **Database:** Migrate PostgreSQL to a managed service like AWS RDS or GCP Cloud SQL (with the pgvector extension enabled).
*   **Backend:** Containerize the FastAPI app and deploy it to a serverless platform like AWS ECS Fargate or Google Cloud Run to handle scale to zero and burst traffic easily.
*   **Frontend:** Deploy the Next.js app to Vercel or AWS Amplify.
*   **Data Pipeline:** Move the dbt execution into a managed orchestrator like Airflow or Prefect, rather than running it inside an initialization container.

**Q11: If latency becomes an issue (the Copilot takes 10 seconds to answer), how would you optimize it?**
**Answer:**
1.  **Semantic Caching:** Implement Redis with a vector similarity search (like RedisVL) to cache similar queries. If a user asks a slightly reworded question that we've answered before, we return the cached answer instantly without hitting the LLM.
2.  **Streaming:** Implement Server-Sent Events (SSE) or WebSockets in FastAPI and Next.js to stream the LLM's response tokens to the UI as they are generated, drastically reducing perceived latency.
3.  **Smaller Models:** For simple routing or tool-calling tasks, use a smaller, faster model, and only reserve the heavy model (like Gemini Pro) for complex reasoning or final synthesis.