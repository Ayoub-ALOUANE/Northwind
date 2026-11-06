-- Singular test: every row in fact_sales must have non-negative net_revenue.
-- A negative net_revenue would indicate corrupted pricing or discount data.
-- This test FAILS (returns rows) if any violation exists.

SELECT
    order_id,
    product_id,
    net_revenue,
    gross_revenue,
    discount
FROM {{ ref('fact_sales') }}
WHERE net_revenue < 0
