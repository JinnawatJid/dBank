WITH stg_customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
)

SELECT
    customer_id,
    first_name,
    last_name,
    -- PII Masking applied at the database layer (Defense in Depth)
    CONCAT(SUBSTR(email, 1, 3), '***@***.com') AS email_masked,
    CONCAT(SUBSTR(phone, 1, 3), '-***-****') AS phone_masked,
    date_of_birth,
    -- Calculate age broadly to avoid exposing exact DOB, but keep DOB for other uses if needed
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth)) AS age_years,
    join_date,
    customer_segment,
    _ingested_at
FROM stg_customers
