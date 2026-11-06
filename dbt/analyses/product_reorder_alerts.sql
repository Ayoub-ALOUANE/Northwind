-- Products that need restocking: active products where units_in_stock < reorder_level.
-- Operational alert query — run this to flag inventory issues before stockouts occur.

SELECT
    p.product_id,
    p.product_name,
    p.category_name,
    p.supplier_company_name,
    p.supplier_country,

    p.units_in_stock,
    p.reorder_level,
    p.units_on_order,
    (p.reorder_level - p.units_in_stock)                    AS units_deficit,

    -- Estimated net revenue at risk if product goes out of stock
    ROUND(
        (p.reorder_level - p.units_in_stock) * p.unit_price
    ::NUMERIC, 2)                                           AS estimated_revenue_at_risk,

    p.unit_price,
    p.quantity_per_unit

FROM {{ ref('dim_products') }} AS p

WHERE p.discontinued = FALSE
  AND p.units_in_stock < p.reorder_level

ORDER BY units_deficit DESC, estimated_revenue_at_risk DESC
