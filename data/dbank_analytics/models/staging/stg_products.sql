WITH source AS (
    SELECT * FROM {{ source('raw', 'products') }}
)

SELECT
    product_id,
    product_name,
    product_type,
    launch_date,
    _ingested_at
FROM source
