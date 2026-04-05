WITH source AS (
    SELECT * FROM {{ source('raw', 'tickets') }}
)

SELECT
    ticket_id,
    customer_id,
    product_id,
    issue_type,
    status,
    priority,
    created_at,
    resolved_at,
    _ingested_at
FROM source
