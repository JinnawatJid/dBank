{% snapshot customers_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='customer_id',

      strategy='timestamp',
      updated_at='_ingested_at',
    )
}}

select * from {{ ref('stg_customers') }}

{% endsnapshot %}
