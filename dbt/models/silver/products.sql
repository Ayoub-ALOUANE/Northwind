SELECT
    product_id,

    NULLIF(TRIM(product_name), '') AS product_name,

    supplier_id,
    category_id,

    NULLIF(TRIM(quantity_per_unit), '') AS quantity_per_unit,

    unit_price,
    units_in_stock,
    units_on_order,
    reorder_level,

    CASE
        WHEN discontinued = 1 THEN TRUE
        ELSE FALSE
    END AS discontinued,

    _airbyte_extracted_at AS loaded_at

FROM {{ source('bronze', 'products') }}

WHERE product_id IS NOT NULL
  AND unit_price >= 0