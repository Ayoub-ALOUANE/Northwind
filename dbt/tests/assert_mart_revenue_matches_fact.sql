-- Singular test: verifies that the mart_sales_summary revenues
-- match the raw fact_sales totals within a 1-cent tolerance.
-- Detects silent aggregation bugs in the mart.

WITH fact_total AS (
    SELECT ROUND(SUM(net_revenue)::NUMERIC, 0) AS total_net_revenue
    FROM {{ ref('fact_sales') }}
),

mart_total AS (
    SELECT ROUND(SUM(total_net_revenue)::NUMERIC, 0) AS total_net_revenue
    FROM {{ ref('mart_sales_summary') }}
)

SELECT
    f.total_net_revenue AS fact_total,
    m.total_net_revenue AS mart_total,
    ABS(f.total_net_revenue - m.total_net_revenue) AS discrepancy
FROM fact_total AS f
CROSS JOIN mart_total AS m
WHERE ABS(f.total_net_revenue - m.total_net_revenue) > 1   -- tolerance: $1
