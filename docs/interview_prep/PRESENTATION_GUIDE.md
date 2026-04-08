# dData Mission Engineer Interview: Presentation Guide

**Candidate:** Jinnawat Jidsanoa
**Audience:** CTO & Technical Panel
**Time:** 45 minutes (Presentation + Demo) + 15 minutes Q&A

---

## 1. Introduction & The Thought Process (10 minutes)

**Objective:** Hook the CTO immediately by showing your structured thinking process. Prove that you translate business problems into technical architectures, not just blindly writing code.

*   **Greeting:** "สวัสดีครับ วันนี้ผมจะมานำเสนอโปรเจกต์ Deep Insights Copilot ครับ ก่อนที่เราจะไปดูเรื่อง Architecture หรือ Live Demo ผมอยากขอแชร์กระบวนการคิด ของผมสักนิดนึงครับ"
*   **The Approach:** "สิ่งแรกที่ผมทำหลังจากได้รับ Assignment คือการอ่านอย่างตั้งใจและตีความโจทย์ให้แตกครับ"
*   **Requirement Analysis (Referencing the PDF):** "ถ้าเรามาดูใน PDF assignment ในหัวข้อ Scenario ไปพร้อมๆ กันนะครับ พอผมอ่านส่วนแรก ผมก็จับใจความได้ว่า เราเป็น Operation support team ที่มีปัญหาคือ Ticket เปิดมาเยอะมาก และเราต้องการตัวช่วยในเรื่องนี้ ซึ่งก็คือระบบ 'Deep Insights Copilot' โดยเจ้าระบบนี้จะต้องมีความสามารถหลัก 2 อย่างครับ:"
    1.  **"1. answer natural-language questions grounded in company data/docs"**
        *   "คือต้องตอบคำถามโดยอ้างอิงจากข้อมูลและเอกสารจากทางบริษัท ตรงนี้ผมปิ๊งขึ้นมาทันทีว่า นี่แหละคือคอนเซปต์และ Use Case ของการปรับใช้ **RAG (Retrieval-Augmented Generation)** ในธุรกิจจริง เพื่อไม่ให้ AI มั่วคำตอบ (Hallucination)"
    2.  **"2. run safe, parameterized actions (SQL, KPI queries) via MCP tools"**
        *   "ก็คือ RAG ตัวนี้ต้องมีความสามารถในการรันคำสั่ง SQL หรือดึงข้อมูล KPI ผ่านสิ่งที่เรียกว่า MCP Tools... สารภาพตามตรงครับว่าตอนที่อ่านเจอคำนี้ ผมยังไม่มั่นใจ 100% ว่า MCP คืออะไร รู้แค่ว่าเป็นคำศัพท์ที่เพิ่งเริ่มได้ยินบ่อยมาก ผมเลยรีบวงกลมตัวแดงๆ และขอโน้ตไว้ก่อนเลยว่า นี่คือเทคโนโลยีหลักที่ผมต้องไป Research เพิ่มเติมทันที เพื่อนำมาใช้เป็น Core Architecture ของโปรเจกต์นี้ครับ"

*   **Requirement Analysis (Business & Guardrails):** "โอเค ต่อไปเราก็จะมาดูส่วนถัดไป คือเรื่องของ Business Requirements Spec ส่วนสำคัญที่ผมสังเกตเห็นก็คือตัวคำถามตัวอย่างที่ผมต้องใช้ถามกับ RAG อย่างเช่นเรื่อง Top 5 root causes หรือเรื่อง Churned customers"
    *   "และอีกส่วนที่สำคัญมากคือ **AI Guardrails** ครับ ซึ่งโจทย์ระบุชัดเจนว่า 'read-only DB access; PII (Sensitive Data) must be masked; every tool call must be parameterized & logged' ตรงส่วนนี้เป็นเรื่อง Security แบบเจาะลึก ซึ่งผมยอมรับว่าตอนแรกยังไม่มั่นใจนัก ผมเลยวงกลมตัวแดงๆ ไว้เลยว่า นี่คือส่วนที่ผมต้องไปทำ Study Guide และศึกษาเพิ่มอย่างจริงจัง เพื่อนำมาสร้างเป็นฐานของ Architecture โปรเจกต์นี้ให้มีความปลอดภัยระดับ Enterprise ครับ"
*   **Transition:** "...หลังจากทำความเข้าใจโจทย์และศึกษาเรื่อง MCP กับ AI Guardrails เพิ่มเติมแล้ว ผมก็นำ Requirements ทั้งหมดไปแตกเป็นแผนการทำงาน 3 วัน (3-Day Sprint Plan) เพื่อให้เกิดเป็น MVP ที่ใช้งานได้จริงครับ ซึ่งเดี๋ยวเราจะไปดู Architecture ของระบบนี้กันครับ"

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
