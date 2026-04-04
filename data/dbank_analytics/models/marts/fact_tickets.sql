WITH stg_tickets AS (
    SELECT * FROM {{ ref('stg_tickets') }}
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
    -- Provide derived metrics like time-to-resolution
    EXTRACT(EPOCH FROM (resolved_at - created_at))/3600 AS resolution_time_hours,
    _ingested_at
FROM stg_tickets
