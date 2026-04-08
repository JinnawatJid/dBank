# dData Mission Engineer Interview: Presentation Guide

**Candidate:** Jinnawat Jidsanoa
**Audience:** CTO & Technical Panel
**Time:** 45 minutes (Presentation + Demo) + 15 minutes Q&A

---

## 1. Introduction & The Thought Process (10 minutes)

*   **The Approach:** "สิ่งแรกที่ผมทำหลังจากได้รับ Assignment คือการอ่านอย่างตั้งใจและตีความโจทย์ให้แตกครับ"
*   **Requirement Analysis (Referencing the PDF):** "ถ้าเรามาดูใน PDF assignment ในหัวข้อ Scenario ไปพร้อมๆ กันนะครับ พอผมอ่านส่วนแรก ผมก็จับใจความได้ว่า เราเป็น Operation support team ที่มี Ticket เปิดมาเยอะมาก และเราต้องการตัวช่วยในเรื่องนี้ ซึ่งก็คือระบบ 'Deep Insights Copilot' โดยเจ้าระบบนี้จะต้องมีความสามารถหลัก 2 อย่างครับ:"
    1.  **"1. answer natural-language questions grounded in company data/docs"**
        *   "คือต้องตอบคำถามโดยอ้างอิงจากข้อมูลและเอกสารจากทางบริษัท ตรงนี้ผมปิ๊งขึ้นมาทันทีว่า นี่แหละคือคอนเซปต์และ Use Case ของการปรับใช้ RAG ในธุรกิจจริง เพื่อไม่ให้ AI มั่วคำตอบ"
    2.  **"2. run safe, parameterized actions (SQL, KPI queries) via MCP tools"**
        *   "ก็คือ RAG ตัวนี้ต้องมีความสามารถในการรันคำสั่ง SQL หรือดึงข้อมูล KPI ผ่านสิ่งที่เรียกว่า MCP Tools... ตอนที่อ่านเจอคำนี้ ผมยังไม่มั่นใจ 100% ว่า MCP คืออะไร รู้แค่ว่าเป็นคำศัพท์ที่ได้ยินบ่อยมาก ผมเลยรีบวงกลมตัวแดงๆ และขอโน้ตไว้ก่อนเลยว่า นี่คือเทคโนโลยีหลักที่ผมต้องไป Research เพิ่มเติม"

*   **Requirement Analysis (Guardrails):**
    *   "3. และอีกส่วนที่สำคัญมากคือ **AI Guardrails** ครับ ซึ่งโจทย์ระบุชัดเจนว่า 'read-only DB access; PII (Sensitive Data) must be masked; every tool call must be parameterized & logged' ตรงส่วนนี้เป็นเรื่อง Security แบบเจาะลึก ซึ่งเป็นเรื่องที่ผมยังไม่มั่นใจเหมือนกัน ผมเลยวงกลมตัวแดงๆ ไว้เลยว่า นี่คือส่วนที่ผมต้องไปทำ Study Guide และศึกษาเพิ่ม โดยเฉพาะเรื่องของการทำ PII (Sensitive Data)"

*   **Requirement Analysis (What to build):**
    *   "4. ถัดมาคือส่วนของ 'What to build (minimum)' ผมอ่านคร่าวๆ ก็พบเรื่องที่ต้องศึกษาเพิ่มเติมอีก คือเรื่องของ **Data Layer** ที่โจทย์ระบุว่า 'Postgres (star schema or 3NF) + dbt transformations + data tests' ซึ่งเป็นเรื่องของ Data Engineering เต็มตัว และตัวผมเองก็ไม่ได้ทบทวน หรือคุ้นชินกับเรื่องพวกนี้มาสักพักแล้ว ทำให้ผมตระหนักว่า ถ้าจะทำระบบนี้ออกมาให้ดี ผมต้องไปทำ Study Guide และ Re-skill ทบทวนเรื่องพวกนี้ใหม่หมดเลย"
    *   "5. นอกจากนี้ในส่วนของ **Retrieval Layer** โจทย์อนุญาตให้ใช้ 'pgvector' ได้ ซึ่งผมก็โน้ตไว้ว่าต้องไปทำ Study Guide เรื่องนี้เพิ่มเติมเช่นกัน"

*   **Requirement Analysis (Deployment-grade):**
    *   "6. สุดท้ายคือส่วนของ **Deployment-grade (DevOps Engineer track)** ครับ ในส่วนนี้เราคุ้นชินอยู่บ้างแล้ว (เช่น github, containerization, CI) แต่พอเป็น Context ของ AI System ที่ต้องมีเรื่อง observability, secret hygiene, rate limits, circuit breakers รวมไปถึง cost & safety controls ด้วยแล้ว ก็ต้องทำการบ้านเยอะอยู่พอสมควรครับ"

*   **Summary & Next Steps:** "สรุปจากการอ่าน Assignment นะครับ ผมได้ข้อมูลชัดเจนว่า assignment ตัวนี้ต้องประกอบด้วย RAG, การดึงข้อมูลผ่าน Tool, และระบบ Security ที่แน่นหนา สิ่งที่ผมต้องไปทำการบ้านศึกษาเพิ่มอย่างหนักก็คือ MCP, PII Masking, dbt Data Engineering, pgvector และมาตรฐาน Deployment-grade ของ AI

เมื่อเราได้ข้อสรุปของโจทย์แล้ว และ note สำหรับการศึกษาเพิ่มเติม ต่อไปก็จะเป็นการวางแผนครับ"

---

## 2. High-Level Architecture Walkthrough (10 minutes)

*(Note for Jinnawat: For this section, display the "High-Level System Architecture" Mermaid diagram.)*

*   **Transition & Introduction:** "ในส่วนของการออกแบบระบบ ผมได้ออกแบบ High-Level Architecture Diagram ตามภาพนี้ครับ โดยผมแบ่งระบบออกเป็น 3 แกนหลัก คือ User Interface, Backend & API, และ Data Layer ครับ"

*   **1. User Interaction (Next.js & FastAPI):**
    *   "เริ่มจากฝั่งซ้ายบนนะครับ เวลา Operation Support ใช้งานจริง เขาจะพิมพ์คำถามผ่าน UI ที่สร้างด้วย **Next.js** ครับ คำถามนี้จะถูกแพ็คส่งมาเป็น JSON วิ่งเข้ามาที่ **FastAPI Backend** ซึ่งทำหน้าที่เป็นคอยควบคุม Flow ทั้งหมดครับ"
    *   "หน้าตาของ Request Payload ที่ Next.js ส่งมา ก็จะเรียบง่ายแบบนี้เลยครับ:
        ```json
        POST /api/v1/ask
        {
          "query": "What caused the spike in tickets?"
        }
        ```
        และฝั่ง Backend ก็จะตอบกลับมาเป็น JSON ที่มีทั้งคำตอบและรายชื่อ Tools ที่ AI เลือกใช้ครับ หน้าตาประมาณนี้ครับ:
        ```json
        {
          "answer": "The spike in tickets was primarily caused by login failures following the release of Virtual Bank App v1.2.",
          "tools_used": [
            "kpi.top_root_causes",
            "kb.search"
          ]
        }
        ```"

*   **2. LLM & The MCP Engine:**
    *   "พอ FastAPI รับคำถามมา มันจะส่ง Prompt และ Context ไปให้ **Google AI Studio (LLM)** ช่วยคิดครับ ซึ่งในระบบของเรา Context ที่ส่งไปจะถูกกำหนดไว้ใน `system_instruction` เพื่อคุม Persona ของ AI ครับ หน้าตาประมาณนี้:
        ```python
        # Context (System Instruction)
        "You are an expert dBank customer support AI. Provide clear, concise answers... "
        "CRITICAL RULES: Never explicitly mention the names of tools you use..."

        # Prompt (User Query)
        "User: What caused the spike in tickets?"
        ```"
    *   "จุดที่เป็นไฮไลท์คือตรงนี้ครับ LLM ไม่ได้ตอบกลับมาเป็น Text ธรรมดาเสมอไป แต่มันฉลาดพอที่จะบอกว่า 'ฉันต้องดึงข้อมูลเพิ่ม' และมันจะสั่งงานผ่าน **MCP Protocol** กลับมาที่ **MCP Server** ที่ผมสร้างไว้ดักรอคำสั่งโดยเฉพาะครับ"
    *   "โดยใน MCP Server นี้ ผมเตรียม Tool ไว้ 3 ตัวหลักๆ คือ `sql.query` (สำหรับคำถามเจาะจง), `kpi.top_root_causes` (สำหรับดูภาพรวม), และ `kb.search` (สำหรับหาเอกสาร RAG) ครับ"

*   **3. The Data Foundation (dbt & PostgreSQL):**
    *   "ทีนี้มาดูฐานรากของระบบที่ฝั่ง Data Layer ด้านล่างกันบ้างครับ ก่อนที่ Tools พวกนี้จะทำงานได้ เราต้องมีข้อมูลที่พร้อมใช้งานก่อน"
    *   "ผมออกแบบให้ Raw Data ถูกดูดเข้ามา แล้วใช้ **dbt Core** ทำหน้าที่ Transform และ Test ข้อมูลดิบพวกนี้ให้กลายเป็นข้อมูลที่สะอาดและพร้อมใช้ (Marts) เข้าไปเก็บใน **PostgreSQL** ครับ"
    *   "ส่วนพวกไฟล์เอกสาร Knowledge Base ต่างๆ ผมก็เขียน Script ไปทำ Vector Embeddings และยิงเข้าไปเก็บใน PostgreSQL ผ่าน Extension pgvector ครับ"

*   **4. Security Guardrails & Tool Execution:**
    *   "สุดท้าย เมื่อ Tool จาก MCP Server วิ่งไปดึงข้อมูลจาก Database ผมตั้งกฎเหล็ก (Guardrails) ไว้เลยว่า การคิวรีทุกครั้งต้องเป็นแบบ **'Read-Only SQL'** เท่านั้น และข้อมูล PII ต่างๆ จะต้องถูก Masking ตั้งแต่ชั้น FastAPI ก่อนที่ข้อมูลจะหลุดไปถึง LLM ครับ"

*   **Conclusion:** "สรุปก็คือ Architecture ตัวนี้ทำงานประสานกันตั้งแต่ Data Pipeline ขึ้นไปจนถึง UI โดยมี RAG และ MCP เป็นหัวใจหลักในการหาคำตอบ ภายใต้ Security Guardrails ที่รัดกุมครับ"

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
