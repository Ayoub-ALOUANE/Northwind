{% snapshot products_snapshot %}

{{
    config(
        target_schema = 'snapshots',
        unique_key    = 'product_id',
        strategy      = 'check',
        check_cols    = ['unit_price', 'units_in_stock', 'units_on_order', 'discontinued', 'reorder_level']
    )
}}

SELECT
    product_id,
    product_name,
    supplier_id,
    category_id,
    quantity_per_unit,
    unit_price,
    units_in_stock,
    units_on_order,
    reorder_level,
    discontinued
FROM {{ source('bronze', 'products') }}

{% endsnapshot %}
