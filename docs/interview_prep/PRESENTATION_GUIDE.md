# dData Mission Engineer Interview: Presentation Guide

**Candidate:** Jinnawat Jidsanoa
**Audience:** CTO & Technical Panel
**Time:** 45 minutes (Presentation + Demo) + 15 minutes Q&A

---

## 1. High-Level System Architecture (10 minutes)

*(Note for Jinnawat: For this section, you should display the "High-Level System Architecture" diagram. Keep the tone conversational, focusing on the big picture and business value before diving into the code later.)*

*   **The Business Problem:** "สวัสดีครับ ก่อนที่เราจะลงลึกไปที่ Architecture ผมขอเล่าถึงภาพรวมของโจทย์ที่เรากำลังแก้กันก่อนนะครับ จาก Scenario ที่ได้มา ปัญหาหลักของเราคือ Operation support team มี Ticket เปิดเข้ามาเยอะมาก เราจึงต้องการระบบ 'Deep Insights Copilot' เพื่อมาช่วยลดภาระตรงนี้ครับ"
*   **The Solution (Overview):** "ผมเลยออกแบบระบบนี้โดยตั้งเป้าให้มันเป็น 'ผู้ช่วยที่ฉลาด ปลอดภัย และอ้างอิงข้อมูลได้จริง' ซึ่งเพื่อที่จะบรรลุเป้าหมายนี้ ผมได้วางโครงสร้าง Architecture หลักออกเป็น 3 แกน หรือ 3 Pillars หลักๆ ครับ:"

    1.  **"Pillar ที่ 1: Contextual Intelligence (RAG)"**
        *   "สิ่งแรกคือ AI ต้องไม่มั่วครับ มันต้องตอบคำถามโดยอ้างอิงจากเอกสารและข้อมูลจริงของบริษัท ผมเลยใช้ Architecture แบบ RAG โดยมีฐานข้อมูล pgvector เป็นตัวช่วยค้นหาเนื้อหาที่เกี่ยวข้อง"

    2.  **"Pillar ที่ 2: Actionable Insights (MCP)"**
        *   "นอกจากจะตอบคำถามจากเอกสารได้แล้ว ระบบต้องสามารถดึงข้อมูลจริงจาก Database มาตอบได้ด้วย ผมจึงเลือกใช้เทคโนโลยี MCP (Model Context Protocol) มาเป็นสะพานเชื่อมให้ AI สามารถสั่งรัน SQL Query แบบ Read-only ได้อย่างปลอดภัยครับ"

    3.  **"Pillar ที่ 3: Enterprise Security (Guardrails & Data Foundation)"**
        *   "ความปลอดภัยคือเรื่องสำคัญที่สุดครับ ข้อมูลลูกค้าที่เป็น PII ต้องไม่หลุดไปที่ LLM เด็ดขาด ผมเลยสร้าง PII Masking Engine ขึ้นมาดักไว้ นอกจากนี้ในฝั่ง Data Layer ผมใช้ dbt มาช่วยทำ Data Transformation เพื่อให้มั่นใจว่าข้อมูลที่เรานำมาใช้นั้นถูกต้องและพร้อมใช้งานระดับ Production จริงๆ"

*   **Summary:** "สรุปก็คือ Architecture ตัวนี้ไม่ได้ออกแบบมาแค่ให้ทำงานได้แบบ MVP ทั่วไป แต่มันถูกคิดมาแบบ Defense-in-Depth ที่ผสาน RAG เข้ากับ MCP Tools ภายใต้ Security Guardrails ที่รัดกุมครับ เดี๋ยวเรามาเจาะลึกแต่ละส่วนใน Diagram ไปพร้อมๆ กันเลยครับ"

---

## 2. Architecture Walkthrough (10 minutes)

*(Note for Jinnawat: For this section, you should have an Architecture Diagram (e.g., drawn in draw.io or Excalidraw) showing the following boxes and arrows:)*
*   *Box 1 (Left): User -> Next.js (Frontend)*
*   *Box 2 (Middle): FastAPI (Backend) -> PII Masking Engine -> MCP Server Engine*
*   *Box 3 (Top Right): Google AI Studio (LLM)*
*   *Box 4 (Bottom Right): PostgreSQL (Separated into 'raw', 'marts', and 'pgvector' schemas)*
*   *Arrows: Showing the flow from Frontend -> Backend -> Masking -> LLM. Then LLM sending a tool call back to Backend -> Parameterized SQL execution to 'marts'/'pgvector' -> Unmasking -> Back to Frontend.*

*   **Transition & Diagram Introduction:** "เมื่อเราวิเคราะห์ Requirement เสร็จแล้ว สเตปต่อไปคือการออกแบบระบบให้ตอบโจทย์ครับ ซึ่งผมได้วาด High-Level Architecture Diagram ออกมาตามภาพนี้ครับ"
*   **Explaining the Flow (Data Pipeline):** "ผมขอเริ่มอธิบายจากฐานรากของระบบก่อน นั่นคือฝั่ง Data Layer (ชี้ไปที่กล่องล่างขวา) ผมออกแบบโดยยึดหลัก Zero-Trust ครับ ข้อมูลดิบจะถูกดึงเข้ามาที่ schema `raw` ใน Postgres จากนั้นเราจะใช้ dbt ทำการ Transform และ Test ข้อมูลให้กลายเป็น Star Schema ไปเก็บไว้ที่ `marts`... กฎเหล็กของผมคือ AI จะไม่มีวันได้รับสิทธิ์ในการมองเห็น schema `raw` เด็ดขาดครับ"
*   **Explaining the Flow (User Request & Security):** "ทีนี้มาดูเวลา User ใช้งานจริงกันครับ (ชี้ไปที่กล่องซ้าย) พอ User พิมพ์คำถามเข้ามาที่ Next.js มันจะวิ่งมาที่ FastAPI Backend ทันทีที่มาถึง สิ่งแรกที่ผมทำคือส่งมันเข้า **PII Masking Engine** ก่อนเลยครับ ชื่อหรือข้อมูล Sensitive จะถูกแปลงเป็น UUID Token ทันที เพื่อป้องกันไม่ให้ข้อมูลหลุดไปที่ LLM Provider (Google AI)"
*   **Explaining the Flow (MCP & Tool Execution):** "พอ LLM ได้รับคำถาม (ที่ Mask แล้ว) มันจะคิดและบอก Backend ว่า 'ฉันต้องใช้ Tool ชื่อ sql.query' ตรงนี้แหละครับคือการทำงานของ **MCP Server** (ชี้ไปที่กล่องกลาง) ซึ่งผมเขียน Custom ขึ้นมาเพื่อดักจับคำสั่งนี้... ก่อนที่ SQL จะถูกรัน ผมใช้ Pydantic ตรวจสอบความถูกต้องของ Parameters อีกชั้น และบังคับรันผ่าน SQLAlchemy Parameterized queries เท่านั้น เพื่อป้องกัน SQL Injection แบบ 100%"
*   **Conclusion of Architecture:** "สรุปก็คือ Architecture ตัวนี้ไม่ได้ออกแบบมาให้แค่ 'ทำงานได้' แต่มันออกแบบแบบ 'Defense-in-Depth' มี Security Guardrails ดักไว้ทุกๆ จุดเชื่อมต่อ ตั้งแต่ Data Layer ไปจนถึง Prompt Execution ครับ"

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
