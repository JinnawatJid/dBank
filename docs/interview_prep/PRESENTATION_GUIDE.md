# dData Mission Engineer Interview: Presentation Guide

**Candidate:** Jinnawat Jidsanoa
**Audience:** CTO & Technical Panel
**Time:** 45 minutes (Presentation + Demo) + 15 minutes Q&A

---

## 1. Introduction & The Thought Process (10 minutes)

**Objective:** Hook the CTO immediately by showing your structured thinking process. Prove that you translate business problems into technical architectures, not just blindly writing code.

*   **Greeting:** "สวัสดีครับ วันนี้ผมจะมานำเสนอโปรเจกต์ Deep Insights Copilot ครับ ก่อนที่เราจะไปดูเรื่อง Architecture หรือ Live Demo ผมอยากขอแชร์กระบวนการคิด ของผมสักนิดนึงครับ"
*   **The Approach:** "สิ่งแรกที่ผมทำหลังจากได้รับ Assignment คือการอ่านอย่างตั้งใจและตีความโจทย์ให้แตกครับ"
*   **Requirement Analysis (Referencing the PDF):** "ถ้าเรามาดูใน PDF assignment ไปพร้อมๆ กัน ผมได้ไฮไลท์และทำความเข้าใจโจทย์โดยแบ่งเป็น 4 แกนหลัก (Pillars) ตาม Standard Engineering Approach ครับ:"
    1.  **Business Requirements (The "Why"):**
        *   *Highlight:* "Reduce time for Operation support team by 80% and deflect 25% repeat-question tickets."
        *   *Conclusion:* "ผมตีโจทย์ว่าระบบนี้คือ Enterprise Tool สำหรับ User ระดับ 40 ล้านคน ความถูกต้อง (Accuracy) สำคัญที่สุด คำตอบต้อง Grounded กับ Data จริงๆ"
    2.  **Guardrails & Security (The Constraints):**
        *   *Highlight:* "read-only DB access; PII must be masked; every tool call must be parameterized."
        *   *Conclusion:* "นี่คือหัวใจของงาน Corporate Banking ผมรู้ทันทีว่าจะให้ LLM เขียน SQL ไปรันตรงๆ ไม่ได้ ผมจึงต้องทำเรื่อง Reversible PII Masking แบบ Tokenization และบังคับใช้ Parameterized queries เพื่อป้องกัน SQL Injection"
    3.  **Core Architecture (The "How"):**
        *   *Highlight:* "Postgres, dbt, pgvector, MCP server."
        *   *Conclusion:* "ผมแบ่งงานเป็น Layer ชัดเจน ใช้ dbt เพื่อทำ Data Quality Testing (Star Schema) ก่อนที่ LLM จะเห็นข้อมูล ใช้ pgvector เพื่อรวม Relational & Vector ให้อยู่ใน Ecosystem เดียวกัน และเขียน Custom MCP Server เพื่อคุม Execution Flow และความปลอดภัยแบบเบ็ดเสร็จ"
    4.  **Production Readiness (The Delivery):**
        *   *Highlight:* "Deployment-grade, containerization, CI."
        *   *Conclusion:* "ผมตั้งเป้าว่า 'It must be runnable everywhere' จึงทำ Docker Compose ที่ Spin-up ทุกอย่างจบใน Command เดียว และครอบด้วย GitHub Actions ครับ"
*   **Transition:** "จากการวิเคราะห์ 4 แกนนี้ ผมนำไปแตกเป็น 3-Day Sprint Plan เพื่อให้มั่นใจว่าจะส่งมอบ MVP ได้ทันเวลาครับ... ต่อไปเรามาเจาะลึกที่ตัว Architecture กันครับ"

---

## 2. Architecture Walkthrough (10 minutes)

**Objective:** Prove your technical depth based on the requirement analysis.

*   **The Tech Stack in Action:**
    *   **Data Transformation:** Explain how `dbt` acts as the primary quality gate.
    *   **Vector Database:** Explain the efficiency of `pgvector` for this specific scale.
*   **Deep Dive - Security & Zero-Trust (Crucial for CTO):**
    *   "As I mentioned in the requirement analysis, security was paramount."
    *   **Pydantic:** All MCP inputs are strictly typed and validated. Hallucinations fail safely.
    *   **Least Privilege:** The database connection strictly enforces `SET ROLE app_user;`. The LLM can only query read-only, PII-masked marts. Every execution is wrapped in `try/except/finally` blocks with explicit rollbacks to maintain transactional integrity.

---

## 3. The Execution & Post-Mortem Highlights (10 minutes)

**Objective:** Show that you can navigate complex engineering problems and learn from failure. Refer heavily to your `POST_MORTEM.md`.

*   **Transition:** "การวางแผนนั้นสำคัญ แต่การลงมือทำ (Execution) คือจุดที่เราได้เรียนรู้ปัญหาเชิงลึกจริงๆ ครับ"
*   **Highlight 1 - The Vector Dimension Trap:** "For instance, transitioning embedding models caused a dimension mismatch (768 vs 3072). I resolved this by dynamically updating the PostgreSQL schema constraints."
*   **Highlight 2 - PII Masking & Nested Payloads:** "I built a reversible PII masking system. However, I discovered a bug where nested Protobuf objects returned by the LLM caused silent query failures because the unmasking loop wasn't recursive. I had to build a custom unrolling function to deep-traverse and safely unmask nested parameters."
*   **Highlight 3 - Defense-in-Depth:** "I realized protecting data *going to* the LLM wasn't enough. I implemented an 'Output PII Guardrail' that scans the final response before it's sent to the user. If PII is detected, it fails closed, logs a security warning, and directs the user to the CRM. This is the essence of Defense-in-Depth."

---

## 4. Live Demo (10 minutes)

**Objective:** Show the working system proving the concepts discussed.

*   **Setup:** Have `docker-compose up` already running.
*   **Scenario 1: Knowledge Base (RAG)**
    *   **Action:** Ask a question like, "Did ticket volume spike after Virtual Bank App v1.2 release?"
    *   **Talking Point:** "Here, the system uses the `kb.search` MCP tool, querying pgvector."
*   **Scenario 2: Secure SQL Query & KPI Tool**
    *   **Action:** Ask, "Write the SQL for churned customers in the last 30 days." and then "What are the top 5 root causes of product issues?"
    *   **Talking Point:** "Notice the tool execution logs. It safely uses parameterized inputs (`sql.query`) and handles complex aggregations via specific helper tools (`kpi.top_root_causes`)."

---

## 5. Conclusion & Future Scale (5 minutes)

**Objective:** Wrap up strong and show forward-thinking.

*   "To summarize, we achieved a secure, robust MVP that addresses the core business goals outlined in the assignment."
*   **Future Improvements:** "If we were scaling this to production next week, I would focus on:
    1.  **Semantic Caching:** Implementing Redis (RedisVL) to cache frequent queries and reduce LLM costs.
    2.  **Streaming:** Adding SSE (Server-Sent Events) to lower perceived latency.
    3.  **Agentic Frameworks:** Migrating to LangGraph for more complex, multi-agent reasoning steps."
*   "Thank you. I'm happy to dive into any part of the architecture or code."
