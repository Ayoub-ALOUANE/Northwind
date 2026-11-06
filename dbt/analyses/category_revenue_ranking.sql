-- Category performance ranked by net revenue with running total and rank.
-- Shows which product categories drive the majority of Northwind's business.
-- Uses RANK() and cumulative SUM window functions.

WITH category_totals AS (
    SELECT
        category_name,
        ROUND(SUM(total_net_revenue)::NUMERIC, 2)    AS total_net_revenue,
        ROUND(SUM(total_gross_revenue)::NUMERIC, 2)  AS total_gross_revenue,
        ROUND(SUM(total_discount_given)::NUMERIC, 2) AS total_discounts,
        SUM(total_orders)                            AS total_orders,
        SUM(total_units_sold)                        AS total_units_sold,
        ROUND(AVG(avg_discount_pct)::NUMERIC, 2)     AS avg_discount_pct
    FROM {{ ref('mart_sales_summary') }}
    GROUP BY category_name
)

SELECT
    RANK() OVER (ORDER BY total_net_revenue DESC)    AS revenue_rank,
    category_name,
    total_net_revenue,
    total_gross_revenue,
    total_discounts,
    total_orders,
    total_units_sold,
    avg_discount_pct,

    -- Share of total revenue
    ROUND(
        total_net_revenue
        / SUM(total_net_revenue) OVER () * 100
    ::NUMERIC, 1)                                    AS pct_of_total_revenue,

    -- Cumulative revenue (Pareto analysis)
    ROUND(
        SUM(total_net_revenue) OVER (
            ORDER BY total_net_revenue DESC
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) / SUM(total_net_revenue) OVER () * 100
    ::NUMERIC, 1)                                    AS cumulative_revenue_pct

FROM category_totals
ORDER BY revenue_rank
