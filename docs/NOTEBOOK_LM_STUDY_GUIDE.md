# NotebookLM Study Guide: Deep Insights Copilot (Data & Infrastructure)

**Context for NotebookLM:** 
This document outlines the core data engineering and infrastructure concepts implemented in Phase 1 of the "Deep Insights Copilot" project. The user is a Mission Engineer preparing for a presentation to a CTO. They have no prior experience in this field and need to understand the *what*, the *why*, and the *business value* of these concepts to sound like an industry expert.

Please use this document to explain these topics simply, generate practice interview questions, and help the user build a compelling narrative for their presentation.

---

## Topic 1: Vector Databases and RAG (Retrieval-Augmented Generation)
**The Concept:** Traditional databases search by exact keyword match. Vector databases search by "meaning" or "context." RAG is the architecture that allows an AI to read your private company data before answering a question.
**How we implemented it:** We used `pgvector`, an extension for PostgreSQL. We took markdown documents, chopped them into smaller "chunks," converted those chunks into numbers (vectors/embeddings) using Google AI, and stored them in the database.
**Key Terms for NotebookLM to Explain:**
*   Vector Embeddings
*   Cosine Similarity
*   Chunking Strategy (Why overlap chunks?)
*   Why use `pgvector` instead of a standalone vector database like Pinecone? (Hint: Reduces architectural complexity).

## Topic 2: dbt (Data Build Tool) and Analytics Engineering
**The Concept:** Raw data from applications is usually messy and hard to analyze. dbt is the industry-standard tool for transforming data *inside* the database (ELT paradigm) using simple SQL.
**How we implemented it:** We created a two-layer architecture: `staging` (raw data lightly cleaned) and `marts` (business-ready data). 
**Key Terms for NotebookLM to Explain:**
*   ELT (Extract, Load, Transform) vs ETL
*   Data Lineage
*   Why test data before feeding it to an AI? (Hint: "Garbage in, hallucination out").

## Topic 3: Data Modeling (Star Schema & Slowly Changing Dimensions)
**The Concept:** Structuring data so it is fast to query and historically accurate. 
**How we implemented it:** We used a "Star Schema" with Fact tables (events, like tickets) and Dimension tables (nouns, like customers). We implemented Slowly Changing Dimensions (SCD Type 2) using dbt snapshots to track when a customer's data changes over time.
**Key Terms for NotebookLM to Explain:**
*   Fact Tables vs. Dimension Tables
*   Surrogate Keys (Why not just use the normal Customer ID?)
*   Slowly Changing Dimension (SCD) Type 2 (Why is tracking historical changes important for AI reporting?)

## Topic 4: Enterprise Security & Data Privacy (PII)
**The Concept:** Protecting Personally Identifiable Information (PII) in a corporate banking environment. You cannot just send customer names to an external LLM.
**How we implemented it:** We used a "Defense in Depth" strategy. 
1.  **Least Privilege / RBAC (Role-Based Access Control):** The application database user (`app_user`) is physically blocked from reading the raw tables. It can only read the transformed, masked tables.
2.  **Cryptographic Hashing:** Instead of just putting "XXX" over a name, we used SHA-256 one-way hashing for emails and phones. We also used Data Minimization (dropping exact birthdays and calculating age instead).
**Key Terms for NotebookLM to Explain:**
*   Defense in Depth
*   Role-Based Access Control (RBAC)
*   One-way hashing (SHA-256) vs. Two-way encryption
*   Data Minimization

## Topic 5: Infrastructure as Code (IaC) and Performance
**The Concept:** Making sure deployments are reliable, repeatable, and scalable.
**How we implemented it:** We moved database creation scripts into a centralized initialization folder (`db-init/`) rather than running them from application code. We also used "Batch Inserts" to load data instead of row-by-row.
**Key Terms for NotebookLM to Explain:**
*   Idempotency (Why is it important that a script can be run 100 times safely?)
*   Infrastructure as Code (IaC)
*   Batch Processing vs. Row-by-Row Operations

---

### Suggested Prompts to Ask NotebookLM:
1. "Explain 'Slowly Changing Dimensions' to me as if I were a 5th grader, and then explain it again as if I were pitching it to a CTO."
2. "Why is our 'Defense in Depth' PII masking strategy better than just hiding columns in the UI? What risks does it prevent?"
3. "Can you quiz me on the difference between a Fact Table and a Dimension Table?"
4. "Help me draft a 2-minute elevator pitch on why we chose `pgvector` inside PostgreSQL instead of buying a new vector database."