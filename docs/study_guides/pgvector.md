# pgvector: Study Guide for NotebookLM
*(Focus: Vector Databases and PostgreSQL integration for RAG)*

## 1. What is pgvector?
`pgvector` is an open-source extension for PostgreSQL. It allows you to store and query machine learning embeddings (vectors) directly inside your standard PostgreSQL database.

*   **The alternative:** Usually, teams deploy a separate, specialized Vector Database (like Pinecone, Milvus, or Qdrant) just for AI features, while keeping user data in Postgres.
*   **The pgvector advantage:** It eliminates infrastructure complexity. You don't need to manage a second database, handle data syncing between them, or write complex API logic to join user data with AI embeddings. Everything lives inside Postgres.

## 2. Understanding Vectors and Dimensions
To use pgvector, you must understand what an embedding is.
*   **Embeddings:** We take a text document (e.g., a markdown file about dBank's Loan Policy) and pass it through an AI embedding model. The model outputs a massive array of floating-point numbers. This array is the "vector."
*   **Dimensions:** The length of this array is its dimensionality.
    *   Older models (like `text-embedding-004`) output vectors with **768 dimensions**.
    *   Newer, more powerful models (like `models/gemini-embedding-001` used in our project) output vectors with **3072 dimensions**.
*   **The Trap:** When creating the table in PostgreSQL, you must explicitly declare the size. If you declare `embedding vector(768)` but send a 3072-dimension vector, the database will crash.

## 3. How does Search Work? (Cosine Similarity)
When a user asks a question, how does the system find the right document?
1.  The user's question is converted into a vector using the *exact same* embedding model.
2.  We write a SQL query using pgvector's specific operators to compare the "Question Vector" against every "Document Vector" in the database.
3.  **Cosine Similarity (`<=>`):** This is the mathematical algorithm used to measure how "close" two vectors are in multi-dimensional space. The closer the vectors, the more similar the semantic meaning of the text.

**Example pgvector SQL Query:**
```sql
SELECT content, 1 - (embedding <=> :user_question_vector) AS similarity
FROM public.kb_embeddings
ORDER BY embedding <=> :user_question_vector
LIMIT 5;
```
*(This query orders the database rows by mathematical closeness, returning the top 5 most relevant documents).*

## 4. Why pgvector is perfect for the dBank MVP
1.  **Simplicity:** The assignment gave us 5 days. Spinning up a separate Pinecone instance adds DevOps overhead. `pgvector` can be initialized in our existing Docker Compose file with one line: `image: pgvector/pgvector:pg15`.
2.  **ACID Compliance:** Because it's PostgreSQL, our vector inserts are fully transactional. If a data load fails halfway through, Postgres rolls it back safely.
3.  **Hybrid Search Potential:** In the future, we could write a single SQL query that does both semantic search AND relational filtering (e.g., "Find me similar tickets [Vector Search] BUT only where status = 'Open' and customer_segment = 'Premium' [Relational Filter]"). This is incredibly difficult to do if your vectors are in Pinecone and your customer data is in Postgres.