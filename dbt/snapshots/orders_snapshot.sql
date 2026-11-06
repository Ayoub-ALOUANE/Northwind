{% snapshot orders_snapshot %}

{{
    config(
        target_schema = 'snapshots',
        unique_key    = 'order_id',
        strategy      = 'check',
        check_cols    = ['shipped_date', 'ship_via', 'freight', 'ship_name', 'ship_address',
                         'ship_city', 'ship_region', 'ship_postal_code', 'ship_country']
    )
}}

SELECT
    order_id,
    customer_id,
    employee_id,
    order_date,
    required_date,
    shipped_date,
    ship_via,
    freight,
    ship_name,
    ship_address,
    ship_city,
    ship_region,
    ship_postal_code,
    ship_country
FROM {{ source('bronze', 'orders') }}

{% endsnapshot %}
