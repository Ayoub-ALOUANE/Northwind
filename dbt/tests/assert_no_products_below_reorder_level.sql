-- Singular test: products with units_in_stock below reorder_level are flagged.
-- Configured as severity = 'warn' so operational inventory deficits raise awareness without halting ELT.
{{ config(severity = 'warn') }}


SELECT
    product_id,
    product_name,
    units_in_stock,
    reorder_level,
    units_on_order,
    (reorder_level - units_in_stock) AS units_deficit
FROM {{ ref('dim_products') }}
WHERE discontinued = FALSE
  AND units_in_stock < reorder_level
ORDER BY units_deficit DESC
