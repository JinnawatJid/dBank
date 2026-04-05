WITH stg_customers AS (
    SELECT * FROM {{ ref('customers_snapshot') }}
)

SELECT
    dbt_scd_id as customer_key, -- Use the snapshot's unique ID as the surrogate key to handle history
    customer_id,
    first_name,
    last_name,
    -- Strict PII Masking applied at the database layer (Defense in Depth)
    -- Using one-way hashing (SHA-256) instead of string obfuscation
    ENCODE(DIGEST(email, 'sha256'), 'hex') AS email_hash,
    ENCODE(DIGEST(phone, 'sha256'), 'hex') AS phone_hash,
    -- Dropping exact date_of_birth entirely from the marts layer for strict PII compliance
    -- Calculate age broadly to avoid exposing exact DOB
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) AS age_years,
    join_date,
    customer_segment,
    _ingested_at,
    dbt_valid_from,
    dbt_valid_to,
    CASE WHEN dbt_valid_to IS NULL THEN true ELSE false END AS is_current
FROM stg_customers
