WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
)

SELECT
    customer_id,
    first_name,
    last_name,
    email,
    phone,
    date_of_birth,
    join_date,
    customer_segment,
    _ingested_at
FROM source
