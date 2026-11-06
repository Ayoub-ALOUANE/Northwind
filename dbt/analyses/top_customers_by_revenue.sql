-- Top 20 customers by net revenue, with order count and average order value.
-- Use this to identify your most valuable accounts and prioritize retention.

SELECT
    dc.customer_id,
    dc.company_name,
    dc.country,
    dc.city,
    COUNT(DISTINCT fs.order_id)                         AS total_orders,
    SUM(fs.quantity)                                    AS total_units,
    ROUND(SUM(fs.net_revenue)::NUMERIC, 2)              AS total_net_revenue,
    ROUND(SUM(fs.gross_revenue)::NUMERIC, 2)            AS total_gross_revenue,
    ROUND(SUM(fs.discount_amount)::NUMERIC, 2)          AS total_discounts_received,
    ROUND(
        SUM(fs.net_revenue) / NULLIF(COUNT(DISTINCT fs.order_id), 0)
    , 2)                                                AS avg_order_value,
    ROUND(
        SUM(fs.discount_amount) / NULLIF(SUM(fs.gross_revenue), 0) * 100
    , 2)                                                AS overall_discount_pct

FROM {{ ref('fact_sales') }}    AS fs
JOIN {{ ref('dim_customers') }} AS dc ON fs.customer_id = dc.customer_id

GROUP BY dc.customer_id, dc.company_name, dc.country, dc.city
ORDER BY total_net_revenue DESC
LIMIT 20
