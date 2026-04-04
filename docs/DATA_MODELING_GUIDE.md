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

## 3. PII Masking & Defense in Depth

**What is PII?**
Personally Identifiable Information (PII) is any data that can be used to identify a specific individual (e.g., email address, phone number, social security number).

**What is Defense in Depth?**
Defense in Depth is an information security approach where multiple layers of security controls are placed throughout an IT system. If one layer fails, another layer is there to catch the issue.

**Implementation in our project:**
Our PII masking strategy starts at the **Database Layer**. When we transform the raw data into `dim_customers` using dbt, we apply SQL functions to partially mask the sensitive fields:
```sql
CONCAT(SUBSTR(email, 1, 3), '***@***.com') AS email_masked
```
By doing this at the database level, we guarantee that any downstream tool (like our backend API or MCP server) querying the dimensional models will *never* see the full raw PII. This is the first layer of defense.

In the future, the Application Layer (e.g., using Microsoft Presidio) will act as a second layer of defense to scrub any accidental PII that might have been typed into free-text fields (like ticket descriptions).

---

## Further Study Resources

To dive deeper into these concepts, consider the following resources:
*   **Dimensional Modeling:** *The Data Warehouse Toolkit* by Ralph Kimball (The definitive industry textbook on dimensional modeling).
*   **dbt:** [dbt Labs Documentation & Courses](https://courses.getdbt.com/)
*   **PII & Security:** The principle of Least Privilege and OWASP data protection guidelines.