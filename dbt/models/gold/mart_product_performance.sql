{{
    config(
        materialized = 'table',
        schema       = 'gold'
    )
}}

-- ─────────────────────────────────────────────────────────────────────────────
-- mart_product_performance
-- Grain: one row per product
-- Purpose: aggregates all-time sales performance per product for inventory
--          planning, pricing analysis, and category management dashboards.
-- ─────────────────────────────────────────────────────────────────────────────

WITH sales AS (
    SELECT
        fs.product_id,
        fs.order_date_id,
        fs.quantity,
        fs.gross_revenue,
        fs.net_revenue,
        fs.discount_amount,
        fs.discount,
        fs.is_late_shipment
    FROM {{ ref('fact_sales') }} AS fs
),

product_sales AS (
    SELECT
        product_id,
        COUNT(*)                                                AS total_order_lines,
        COUNT(DISTINCT order_date_id)                           AS order_days_active,
        SUM(quantity)                                           AS total_units_sold,
        ROUND(SUM(gross_revenue)::NUMERIC, 2)                   AS total_gross_revenue,
        ROUND(SUM(net_revenue)::NUMERIC, 2)                     AS total_net_revenue,
        ROUND(SUM(discount_amount)::NUMERIC, 2)                 AS total_discount_given,
        ROUND(AVG(net_revenue)::NUMERIC, 2)                     AS avg_line_value,
        ROUND(AVG(quantity)::NUMERIC, 1)                        AS avg_quantity_per_line,
        ROUND(AVG(discount)::NUMERIC, 4)                        AS avg_discount_rate,
        ROUND(
            SUM(discount_amount) / NULLIF(SUM(gross_revenue), 0) * 100
        ::NUMERIC, 2)                                           AS overall_discount_pct,
        SUM(CASE WHEN is_late_shipment = TRUE  THEN 1 ELSE 0 END) AS late_shipments,
        SUM(CASE WHEN is_late_shipment = FALSE THEN 1 ELSE 0 END) AS on_time_shipments,
        MIN(order_date_id)                                      AS first_order_date,
        MAX(order_date_id)                                      AS last_order_date
    FROM sales
    GROUP BY product_id
)

SELECT
    -- ── Product Attributes ────────────────────────────────────────────────────────
    dp.product_id,
    dp.product_name,
    dp.category_name,
    dp.supplier_company_name,
    dp.supplier_country,
    dp.unit_price             AS current_list_price,
    dp.units_in_stock,
    dp.units_on_order,
    dp.reorder_level,
    dp.discontinued,
    CASE
        WHEN dp.units_in_stock = 0        THEN 'Out of Stock'
        WHEN dp.units_in_stock < dp.reorder_level THEN 'Low Stock'
        ELSE                                        'In Stock'
    END                       AS stock_status,

    -- ── Sales Performance ─────────────────────────────────────────────────────────
    ps.total_order_lines,
    ps.total_units_sold,
    ps.total_gross_revenue,
    ps.total_net_revenue,
    ps.total_discount_given,
    ps.avg_line_value,
    ps.avg_quantity_per_line,
    ps.avg_discount_rate,
    ps.overall_discount_pct,
    ps.late_shipments,
    ps.on_time_shipments,
    ROUND(
        ps.late_shipments::NUMERIC
        / NULLIF(ps.late_shipments + ps.on_time_shipments, 0) * 100
    , 1)                      AS late_shipment_rate_pct,

    -- ── Revenue per Unit (sells vs list price comparison) ─────────────────────────
    ROUND(
        ps.total_net_revenue::NUMERIC / NULLIF(ps.total_units_sold, 0)
    , 2)                      AS actual_avg_selling_price,
    ROUND(
        (dp.unit_price - (ps.total_net_revenue::NUMERIC / NULLIF(ps.total_units_sold, 0)))
    , 2)                      AS price_vs_list_gap,

    -- ── Timeline ──────────────────────────────────────────────────────────────────
    ps.first_order_date,
    ps.last_order_date

FROM {{ ref('dim_products') }} AS dp
LEFT JOIN product_sales         AS ps ON dp.product_id = ps.product_id
