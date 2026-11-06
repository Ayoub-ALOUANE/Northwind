{{
    config(
        materialized = 'table',
        schema = 'gold'
    )
}}

WITH sales AS (
    SELECT
        fs.order_date_id,
        fs.gross_revenue,
        fs.net_revenue,
        fs.discount_amount,
        fs.quantity,
        fs.order_id,
        fs.product_id,
        dp.category_name,
        dc.country           AS customer_country,
        dc.city              AS customer_city,
        dd.year,
        dd.quarter,
        dd.month,
        dd.month_name,
        dd.quarter_name,
        dd.year_month
    FROM {{ ref('fact_sales') }} AS fs
    LEFT JOIN {{ ref('dim_products') }}   AS dp ON fs.product_id  = dp.product_id
    LEFT JOIN {{ ref('dim_customers') }}  AS dc ON fs.customer_id = dc.customer_id
    LEFT JOIN {{ ref('dim_date') }}       AS dd ON fs.order_date_id = dd.date_id
)

SELECT
    -- ── Time Grain ───────────────────────────────────────────────────────────────
    year,
    quarter,
    quarter_name,
    month,
    month_name,
    year_month,

    -- ── Dimensions ───────────────────────────────────────────────────────────────
    category_name,
    customer_country,

    -- ── Volume Metrics ───────────────────────────────────────────────────────────
    COUNT(DISTINCT order_id)                                            AS total_orders,
    COUNT(DISTINCT product_id)                                          AS distinct_products_sold,
    SUM(quantity)                                                       AS total_units_sold,

    -- ── Revenue Metrics ───────────────────────────────────────────────────────────
    ROUND(SUM(gross_revenue)::NUMERIC, 2)                               AS total_gross_revenue,
    ROUND(SUM(net_revenue)::NUMERIC, 2)                                 AS total_net_revenue,
    ROUND(SUM(discount_amount)::NUMERIC, 2)                             AS total_discount_given,

    -- ── Averages ─────────────────────────────────────────────────────────────────
    ROUND(AVG(net_revenue)::NUMERIC, 2)                                 AS avg_order_line_value,
    ROUND(
        CASE WHEN SUM(gross_revenue) = 0 THEN 0
             ELSE SUM(discount_amount) / SUM(gross_revenue) * 100
        END::NUMERIC, 2
    )                                                                   AS avg_discount_pct

FROM sales
GROUP BY
    year, quarter, quarter_name, month, month_name, year_month,
    category_name, customer_country
