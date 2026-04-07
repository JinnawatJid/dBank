# Data Modeling Guide

This document provides a deep dive into the industry-standard data engineering practices implemented in this project, specifically regarding Data Transformations, the Star Schema, Dimensional Modeling, and PII Masking. It also serves as reference material to help explain these concepts to stakeholders.

---

## 1. Data Transformations (dbt)

**What is it?**
Data Transformation is the process of taking raw, ingested data and changing its format, structure, or values so that it is optimized for analysis and querying.

**Why do we do it?**
Raw data from operational systems (like the CSVs from our backend scripts) is often messy, lacks strict constraints, or exposes sensitive information. By transforming it, we enforce business logic, clean the data, and prepare it for efficient reporting.

In this project, we use **dbt (data build tool)**. dbt is the industry standard for transforming data *within* the database using SQL. It allows data engineers to write modular SQL queries (models), test the data (e.g., ensuring IDs are unique), and automatically handle the creation of tables and views.

## 2. Dimensional Modeling & Star Schema

**What is it?**
Dimensional modeling is a design technique for data warehouses. The most common form is the **Star Schema**, which divides data into two types of tables:
1.  **Fact Tables:** Store quantitative, transactional data (the "events" or "measurements"). They contain foreign keys that link to dimension tables. Examples: Orders, Support Tickets, Logins.
2.  **Dimension Tables:** Store descriptive attributes (the "context"). They contain a primary key and descriptive fields. Examples: Customers, Products, Time.

When visualized, the Fact table sits in the center, surrounded by the Dimension tables, resembling a star.

**Implementation in our project:**
*   **`fact_tickets`**: Holds the transactional records of support tickets being created and resolved.
*   **`dim_customers`**: Holds the descriptive context about who the customer is (age, segment).
*   **`dim_products`**: Holds the descriptive context about the products involved in the tickets.

**Why do we do it?**
*   **Performance:** Queries for analytical reporting (aggregating tickets by customer segment or product type) are much faster because the structure is optimized for read-heavy operations.
*   **Simplicity:** It provides a highly intuitive model for business analysts to understand. They just join the central Fact to the surrounding Dimensions.

## 3. Strict PII Masking & Defense in Depth

**What is PII?**
Personally Identifiable Information (PII) is any data that can be used to identify a specific individual (e.g., email address, phone number, social security number). In corporate banking, compliance with regulations like GDPR or CCPA demands strict data minimization.

**Implementation in our project:**
Our PII masking strategy starts at the **Database Layer**. When transforming raw data into `dim_customers` using dbt, we apply strict corporate standards:
1.  **Data Minimization:** We drop the exact `date_of_birth` entirely in the analytical layer and only expose a derived `age_years`.
2.  **One-Way Hashing:** Instead of easily decipherable string obfuscation (like `***@***.com`), we use cryptographic SHA-256 hashing for emails and phone numbers.
```sql
ENCODE(DIGEST(email, 'sha256'), 'hex') AS email_hash
```
This ensures downstream systems can still count unique users (as the hash is consistent) without ever exposing the raw PII.

**Strict Database Roles (Least Privilege)**
To enforce this, we use distinct database users:
*   `dbt_user`: Has access to the `raw` schema to read raw data and write to the `marts` schema.
*   `app_user`: The backend application connects using this user, which *only* has read-access to the `marts` schema. It is physically impossible for the application to query the unmasked raw data.

In the future, the Application Layer (e.g., using Microsoft Presidio) will act as a second layer of defense to scrub any accidental PII typed into free-text fields (like ticket descriptions).

## 4. Surrogate Keys

**What are Surrogate Keys?**
Instead of relying on the natural key from the source system (e.g., `customer_id = 'CUST-00001'`), a data warehouse typically generates its own primary key, known as a Surrogate Key.

**Implementation:**
We use the `dbt_utils.generate_surrogate_key` macro to create an MD5 hash of the natural keys, generating columns like `customer_key`, `product_key`, and `ticket_key`. This isolates the data warehouse from changes in the source system (e.g., if the backend decides to change the format of customer IDs) and ensures consistent performance for joins.

## 5. Slowly Changing Dimensions (SCD Type 2)

**What is SCD Type 2?**
In analytics, you often need to track historical changes. If a customer upgrades from the 'Retail' segment to 'Wealth', you don't want to just overwrite their old segment, because past analytical reports would retroactively change. SCD Type 2 solves this by creating a new row for every change, tracking validity dates.

**Implementation:**
We utilize dbt's **Snapshots** feature (`snapshots/customers_snapshot.sql`). It tracks changes to the `stg_customers` model. When the mock data script updates a customer's segment, the snapshot automatically expires the old record (sets `dbt_valid_to`) and inserts the new record. `dim_customers` then reads from this snapshot, providing analysts with a complete history of the customer's attributes over time.

---

## Further Study Resources

To dive deeper into these concepts, consider the following resources:
*   **Dimensional Modeling:** *The Data Warehouse Toolkit* by Ralph Kimball (The definitive industry textbook on dimensional modeling).
*   **dbt:** [dbt Labs Documentation & Courses](https://courses.getdbt.com/)
*   **PII & Security:** The principle of Least Privilege and OWASP data protection guidelines.