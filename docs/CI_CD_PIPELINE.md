# Deep Insights Copilot - CI/CD Pipeline Architecture

## Overview
This repository uses a **Continuous Integration (CI)** pipeline powered by **GitHub Actions** (`.github/workflows/ci.yml`).

The purpose of this pipeline is to guarantee that the application, database, and data transformation logic (`dbt`) are always stable, reproducible, and ready for deployment. It ensures no code breaks our strict security or data integrity standards before merging into the `main` branch.

---

## How It Works (Step-by-Step)

Every time code is pushed or a Pull Request is opened against the `main` branch, GitHub provisions a fresh, isolated Ubuntu virtual machine and automatically executes the following sequence:

### 1. Database Provisioning & Security Setup
* **Action:** The pipeline spins up a fresh PostgreSQL database container (`pgvector/pgvector:pg15`).
* **Verification:** It executes `db-init/init-user.sh` and `db-init/init-kb-schema.sh`.
* **Why:** This proves that our **Zero-Trust Least Privilege** model works. It verifies that the initialization scripts correctly create the `raw`, `marts`, `snapshots`, and `kb` schemas, and that the `dbt_user` (read/write) and `app_user` (read-only) roles are accurately assigned.

### 2. Mock Data Injection
* **Action:** The pipeline executes `scripts/generate_mock_data.py`.
* **Verification:** Generates thousands of rows of realistic corporate banking data (customers, tickets, products, logins) and pushes it into the `raw` database schema.
* **Why:** This provides a standardized baseline of data so all subsequent tests have realistic scenarios to evaluate against.

### 3. Knowledge Base Embedding Generation
* **Action:** The pipeline executes `scripts/embed_kb.py`.
* **Verification:** Parses all markdown files in `data/kb/`, chunks them, and generates dummy 768-dimensional fallback embeddings.
* **Why:** Ensures that the vector database (`pgvector`) is capable of accepting batch inserts and that the fallback API logic correctly handles environments without active Google API keys.

### 4. Data Warehouse Transformation (`dbt`)
* **Action:** The pipeline changes directory to `data/dbank_analytics` and executes:
  1. `dbt deps` (Installs data packages)
  2. `dbt run --models staging` (Builds `stg_` views)
  3. `dbt snapshot` (Captures Slowly Changing Dimensions history)
  4. `dbt run` (Builds final `dim_` and `fact_` tables using Reversible PII Masking)
* **Why:** This proves our data transformation DAG (Directed Acyclic Graph) is mathematically correct and that no views or dependencies are broken.

### 5. Automated Data Quality Testing
* **Action:** The pipeline executes `dbt test`.
* **Verification:** Runs 8 rigorous assertions against the data.
* **Why:** It mathematically proves the data has no duplicates (`unique`) and no missing IDs (`not_null`), guaranteeing downstream dashboards and the LLM tools never ingest corrupted datasets.

### 6. Backend API & MCP Server Testing (`pytest`)
* **Action:** The pipeline executes `pytest backend/tests`.
* **Verification:** Runs unit and integration tests against the FastAPI backend and Model Context Protocol (MCP) server.
* **Why:** Ensures our LLM orchestration, global error handlers, dynamic parameterized SQL query tools, and Knowledge Base search tools function correctly under strict `OBJECT`, `STRING`, and `INTEGER` JSON-schema typings.

---

## Independent Autonomous Verification
This pipeline serves as an **independent, automated audit**.

Instead of relying on a developer stating "It works on my machine", this pipeline proves the code works in a pristine, production-like environment. If any of the above steps fail (e.g., a broken SQL join, a failed security grant, or a missing Python dependency), GitHub will flag the build with a red ❌.

The AI Engineer (Jules) is deeply integrated with GitHub Actions. When a Check Suite Failure occurs, the agent automatically receives the logs, identifies the root cause, and pushes an autonomous fix without manual user intervention.
