-- Month-over-month revenue growth using LAG window function.
-- Shows which months had the highest growth spikes and which had declines.
-- Key metric for identifying seasonality in the Northwind trading business.

WITH monthly_revenue AS (
    SELECT
        year,
        month,
        month_name,
        year_month,
        ROUND(SUM(total_net_revenue)::NUMERIC, 2)    AS net_revenue,
        SUM(total_orders)                            AS total_orders
    FROM {{ ref('mart_sales_summary') }}
    GROUP BY year, month, month_name, year_month
    ORDER BY year_month
)

SELECT
    year,
    month,
    month_name,
    year_month,
    net_revenue,
    total_orders,

    LAG(net_revenue) OVER (ORDER BY year_month)      AS prev_month_revenue,

    ROUND(
        (net_revenue - LAG(net_revenue) OVER (ORDER BY year_month))
        / NULLIF(LAG(net_revenue) OVER (ORDER BY year_month), 0) * 100
    ::NUMERIC, 1)                                    AS mom_growth_pct,

    SUM(net_revenue) OVER (
        PARTITION BY year ORDER BY month
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )                                                AS ytd_revenue

FROM monthly_revenue
ORDER BY year_month
