# RAG (Retrieval-Augmented Generation): Study Guide for NotebookLM

## What is RAG?
RAG stands for **Retrieval-Augmented Generation**. It is an AI framework that improves the quality of Large Language Model (LLM) generated responses by grounding the model on external sources of knowledge.

*   **The Problem it Solves:** Traditional LLMs only know what they were trained on up to a specific date. If you ask them a highly specific, proprietary company question (e.g., "What is dBank's policy for unlocking a Digital Lending account in 2026?"), the LLM will likely "hallucinate" (make up a plausible but incorrect answer) because it doesn't have that specific data.
*   **The RAG Solution:** Instead of just asking the LLM to guess, RAG forces the system to first **Retrieve** the correct document from a database, and then **Augment** the prompt by giving that document to the LLM, finally asking the LLM to **Generate** an answer *based only on that document*.

## How RAG works (The 3 Steps)

1.  **Retrieval (การดึงข้อมูล):**
    *   When a user asks a question, the system converts the question into a mathematical vector (an "embedding").
    *   It searches a Vector Database to find documents with similar mathematical vectors (semantic similarity).
    *   *dBank Context:* We use `models/gemini-embedding-001` to create embeddings, and PostgreSQL with the `pgvector` extension as our Vector Database.
2.  **Augmentation (การเสริมข้อมูล):**
    *   The system takes the user's original question AND the text from the documents found in step 1.
    *   It creates a new, massive "Prompt" that looks like this: *"Context: [Insert Document Text Here]. Question: [User's Question]. Answer the question using ONLY the context provided."*
3.  **Generation (การสร้างคำตอบ):**
    *   The LLM reads this augmented prompt. Because the answer is literally right there in the context, the LLM can easily summarize it and respond accurately in natural language.
    *   *dBank Context:* We use `gemma-4-31b-it` to read the context and generate the final answer for the Operation Support team.

## Why is RAG critical for Corporate Banking?
*   **Grounding (อ้างอิงได้จริง):** In banking, a wrong answer can lead to financial loss or regulatory fines. RAG ensures the AI is "grounded" in approved company policies, not internet rumors.
*   **Auditability:** Because RAG retrieves specific documents, you can always show the user *where* the AI got its answer from (e.g., "Source: Lending Policy v1.2.pdf").
*   **Security/Access Control:** You can control what the LLM knows based on the user's permissions. If a user doesn't have access to HR files, the Retrieval step simply won't pull HR files, meaning the LLM can't answer HR questions for that user.

## Important Terminology for NotebookLM
*   **Embeddings:** Translating text into arrays of numbers (vectors) so computers can measure how "close" in meaning two sentences are.
*   **Vector Database (Vector Store):** A specialized database (like `pgvector`, Pinecone, or Milvus) designed to store and quickly search massive arrays of embeddings using algorithms like Cosine Similarity.
*   **Chunking:** You can't fit a 500-page PDF into an LLM's prompt. Chunking is the process of breaking large documents into smaller paragraphs (e.g., 500 words each) before embedding them, so you only retrieve the specific paragraph that contains the answer.