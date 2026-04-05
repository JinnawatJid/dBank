WITH stg_tickets AS (
    SELECT * FROM {{ ref('stg_tickets') }}
),
dim_customers AS (
    SELECT * FROM {{ ref('dim_customers') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['t.ticket_id']) }} as ticket_key,
    t.ticket_id,
    -- Perform a point-in-time join to get the correct customer_key based on when the ticket was created
    c.customer_key,
    t.customer_id,
    {{ dbt_utils.generate_surrogate_key(['t.product_id']) }} as product_key,
    t.product_id,
    t.issue_type,
    t.status,
    t.priority,
    t.created_at,
    t.resolved_at,
    -- Provide derived metrics like time-to-resolution
    EXTRACT(EPOCH FROM (t.resolved_at - t.created_at))/3600 AS resolution_time_hours,
    t._ingested_at
FROM stg_tickets t
LEFT JOIN dim_customers c
    ON t.customer_id = c.customer_id
    AND t.created_at >= c.dbt_valid_from
    AND t.created_at < COALESCE(c.dbt_valid_to, '9999-12-31'::timestamp)
