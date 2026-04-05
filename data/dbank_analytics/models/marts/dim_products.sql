WITH stg_products AS (
    SELECT * FROM {{ ref('stg_products') }}
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['product_id']) }} as product_key,
    product_id,
    product_name,
    product_type,
    launch_date,
    _ingested_at
FROM stg_products
