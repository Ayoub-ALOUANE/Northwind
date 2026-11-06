-- RFM segment revenue distribution — answers: "how much revenue does each segment generate?"
-- Useful for prioritizing customer success and marketing budget allocation.

SELECT
    customer_segment,
    COUNT(*)                                            AS customer_count,
    ROUND(SUM(total_net_revenue)::NUMERIC, 2)           AS total_segment_revenue,
    ROUND(AVG(total_net_revenue)::NUMERIC, 2)           AS avg_revenue_per_customer,
    ROUND(AVG(total_orders)::NUMERIC, 1)                AS avg_orders_per_customer,
    ROUND(AVG(recency_days)::NUMERIC, 0)                AS avg_recency_days,
    ROUND(AVG(avg_discount_rate)::NUMERIC, 4)           AS avg_discount_rate,
    ROUND(
        SUM(total_net_revenue)
        / SUM(SUM(total_net_revenue)) OVER () * 100
    ::NUMERIC, 1)                                       AS pct_of_total_revenue

FROM {{ ref('mart_customer_segments') }}
GROUP BY customer_segment
ORDER BY total_segment_revenue DESC
