# Data Engineering: Study Guide for NotebookLM
*(Focus: Postgres, Star Schema/3NF, dbt transformations, and data tests)*

## 1. Data Modeling: Star Schema vs. 3NF
Before feeding data to an AI, it must be structured logically in a database (like PostgreSQL). There are two standard ways to do this in data engineering:

*   **3NF (Third Normal Form):**
    *   *What it is:* Highly normalized data. This means data is split into many small tables to ensure there is zero duplication (redundancy).
    *   *Pros:* Great for operational systems (OLTP) because updating a user's address only happens in one place.
    *   *Cons:* Terrible for AI/Analytics because to answer a simple question, you must `JOIN` 10 different tables, which is slow and complex for an LLM to write.
*   **Star Schema (Dimensional Modeling):**
    *   *What it is:* Data is denormalized into two types of tables:
        1.  **Fact Tables:** Measurements and metrics (e.g., `fact_tickets` containing ticket_id, created_at, resolution_time).
        2.  **Dimension Tables:** Context (e.g., `dim_customers` containing customer_name, segment, location).
    *   *Why it's better for the dBank AI:* It looks like a star (Facts in the middle, Dimensions radiating out). It requires fewer `JOIN`s. When the LLM needs to know "Which customer segment has the most tickets?", a Star Schema makes the SQL incredibly simple and fast.

## 2. dbt (data build tool) Transformations
In modern Data Engineering, we don't write messy Python scripts or raw stored procedures to transform data. We use **dbt**.

*   **What is dbt?** It is a framework that allows data engineers to write SQL `SELECT` statements, and dbt handles the heavy lifting of wrapping those `SELECT`s into `CREATE TABLE` or `CREATE VIEW` commands in PostgreSQL. It treats "SQL as Software."
*   **The dbt Workflow in dBank:**
    1.  **Raw Layer:** Ingest raw CSV files (customers, tickets, products) directly into Postgres without changing them.
    2.  **Staging Models (`staging`):** Write dbt SQL to clean the raw data (e.g., rename columns, cast string dates to timestamp, handle nulls).
    3.  **Mart Models (`marts`):** Write dbt SQL to join the clean staging tables into our final **Star Schema** (the `fact_tickets` and `dim_customers`).
*   *Security Note:* In our project, the AI (`app_user`) is ONLY allowed to query the `marts` layer. It is forbidden from seeing the `raw` layer.

## 3. Data Tests (Ensuring AI Accuracy)
If you feed garbage data into an LLM, it will confidently give garbage answers (Hallucination). dbt allows us to write **Data Tests** to prove our data is clean.

*   **Out-of-the-box dbt Tests:** We configure `.yml` files to test:
    *   `unique`: Ensures no duplicate customer IDs.
    *   `not_null`: Ensures critical fields (like `ticket_status`) are never blank.
    *   `accepted_values`: Ensures a ticket status is only ever "Open", "Closed", or "Pending" (and not a typo like "Clozed").
*   **Why this matters for the Interview:** When the CTO asks "How do you know the AI's answer is correct?", you answer: "Because the LLM is only allowed to query the `marts` schema, and that schema has passed hundreds of automated dbt data tests ensuring complete referential integrity."

## 4. Slowly Changing Dimensions (SCD Type 2) & dbt Snapshots
*   *The Problem:* If a customer upgrades from "Standard" to "Premium" tier today, and we look at a ticket they opened *last month*, was it a Standard ticket or a Premium ticket? If we just overwrite the database (Type 1), we lose history.
*   *The dbt Solution:* **dbt Snapshots**. This implements SCD Type 2. dbt automatically tracks changes over time by adding `dbt_valid_from` and `dbt_valid_to` columns. This allows the AI to accurately answer historical queries.