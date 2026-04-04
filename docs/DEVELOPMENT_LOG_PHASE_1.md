# Development Log - Phase 1: Data Infrastructure & Mocking

This document outlines the engineering decisions and industry-standard practices implemented during the completion of **Task 1.1 (Environment Setup)** and **Task 1.2 (Mock Data Generation)** for the Deep Insights Copilot project. It is intended to serve as a technical supplement for presentation to the CTO.

## 1. Environment Setup (Task 1.1)

### 1.1 Containerization strategy
We utilized `docker-compose` as our primary orchestration tool to ensure parity between local development and future production deployments.
* **Database Choice:** We selected the `pgvector/pgvector:pg15` image. This extends standard PostgreSQL 15 with vector similarity search capabilities, which is crucial for our Retrieval-Augmented Generation (RAG) architecture later in the project without needing a separate standalone vector database like Pinecone.
* **Credentials Management:** Hardcoding passwords in infrastructure files is a critical security risk. We utilized environment variables injected via a `.env` file to manage all database credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`).

### 1.2 Dependency Isolation
We strictly adhered to a monorepo structure, isolating Python dependencies in `backend/requirements.txt`. We pinned major library versions (e.g., `fastapi==0.109.2`, `dbt-postgres==1.7.9`) to ensure deterministic builds and prevent the "it works on my machine" anti-pattern.

## 2. Mock Data Generation (Task 1.2)

### 2.1 Synthetic Data Generation (`Faker`)
To accurately simulate a corporate banking environment without violating real customer data privacy, we engineered a Python script utilizing the `Faker` library.
* **Realistic Distributions:** The script generates relational CSVs (`customers.csv`, `products.csv`, `tickets.csv`, `logins.csv`) with logical links (e.g., tickets tied to valid customer and product IDs). We scaled the data to a realistic volume (e.g., 10,000 logins, 5,000 tickets) to demonstrate application performance under load.

### 2.2 Enterprise Database Standards
When migrating the synthetic data into the `raw` schema in PostgreSQL, we prioritized robust, enterprise-grade data engineering principles over a simple naive insertion:

#### A. Timezone Consistency (`TIMESTAMPTZ`)
Standard `TIMESTAMP` types in PostgreSQL do not enforce timezone awareness, which causes critical failures in globally distributed banking systems. We updated the data generation script and SQL schemas to strictly use `TIMESTAMPTZ` (Timestamp with Time Zone), ensuring all event logs (like ticket creation or login attempts) are universally anchored to UTC.

#### B. Data Lineage and Auditing (`_ingested_at`)
Data lakes and data warehouses require strict auditing to track data freshness and trace errors. We injected an `_ingested_at TIMESTAMPTZ DEFAULT NOW()` column into every raw table definition. This allows data engineers to trace exactly when a batch of synthetic data was appended to the database.

#### C. Bulk Insertion Efficiency
Instead of utilizing slow `INSERT INTO` loops or heavy ORMs like Pandas for ingestion, we utilized PostgreSQL's native `COPY` command via `psycopg2`. This is the industry-standard method for bulk-loading CSVs, offering significantly better throughput and lower memory consumption.

## 3. Security & Governance

### 3.1 The Principle of Least Privilege
By default, the `admin` user handles table creation and schema definitions. However, our application backend should never have destructive access.
* We automated the creation of a `dbank_readonly` user.
* Upon successful data ingestion, the Python script explicitly grants `USAGE` on the `raw` schema and `SELECT` on all tables to this read-only user.
* **Business Impact:** This mitigates the risk of SQL injection attacks from the LLM dropping tables or altering customer data.

### 3.2 Defense in Depth (PII Masking Strategy)
A common pitfall is to heavily mask data at the raw ingestion layer. We intentionally chose to load the raw mock data **unmasked**.
* **Why?** In an enterprise data architecture, raw data is heavily locked down (only accessible to administrators). The masking must happen dynamically downstream.
* **Our Strategy:** By leaving the raw data intact, we set the stage to demonstrate a sophisticated "Defense in Depth" strategy:
    1. **Database Layer:** We will use `dbt` to create transformed views that hash or drop explicit PII before analysts see it.
    2. **Application Layer:** We will utilize Microsoft Presidio in the FastAPI backend to scrub natural language text before it is sent to the LLM.
This layered approach proves to the CTO that we understand modern data governance.
