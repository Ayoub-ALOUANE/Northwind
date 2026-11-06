{{
    config(
        materialized = 'table',
        schema       = 'gold'
    )
}}

-- ─────────────────────────────────────────────────────────────────────────────
-- mart_customer_segments
-- Grain: one row per customer (all-time)
-- Purpose: RFM-style customer segmentation for CRM and marketing analytics.
--          Computes Recency, Frequency, Monetary value and assigns a segment label.
-- ─────────────────────────────────────────────────────────────────────────────

WITH customer_stats AS (
    SELECT
        fs.customer_id,
        COUNT(DISTINCT fs.order_id)                                         AS frequency,
        SUM(fs.net_revenue)                                                 AS monetary,
        MAX(fs.order_date_id)                                               AS last_order_date,
        MIN(fs.order_date_id)                                               AS first_order_date,
        COUNT(DISTINCT DATE_TRUNC('month', fs.order_date_id::DATE))         AS active_months,
        COUNT(DISTINCT fs.product_id)                                       AS unique_products,
        COUNT(DISTINCT dp.category_name)                                    AS unique_categories,
        ROUND(AVG(fs.net_revenue)::NUMERIC, 2)                              AS avg_line_value,
        ROUND(SUM(fs.net_revenue)::NUMERIC / NULLIF(COUNT(DISTINCT fs.order_id), 0), 2)
                                                                            AS avg_order_value,
        ROUND(AVG(fs.discount)::NUMERIC, 4)                                 AS avg_discount_rate,
        -- Recency: days since last order (relative to dataset max date)
        (DATE '1998-12-31' - MAX(fs.order_date_id::DATE))::INT              AS recency_days
    FROM {{ ref('fact_sales') }}   AS fs
    LEFT JOIN {{ ref('dim_products') }} AS dp ON fs.product_id = dp.product_id
    GROUP BY fs.customer_id
),

percentiles AS (
    SELECT
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY monetary)    AS monetary_p33,
        PERCENTILE_CONT(0.66) WITHIN GROUP (ORDER BY monetary)    AS monetary_p66,
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY frequency)   AS freq_p33,
        PERCENTILE_CONT(0.66) WITHIN GROUP (ORDER BY frequency)   AS freq_p66,
        PERCENTILE_CONT(0.33) WITHIN GROUP (ORDER BY recency_days) AS recency_p33,
        PERCENTILE_CONT(0.66) WITHIN GROUP (ORDER BY recency_days) AS recency_p66
    FROM customer_stats
),

scored AS (
    SELECT
        cs.*,
        -- Monetary score (3=highest spend)
        CASE
            WHEN cs.monetary >= p.monetary_p66  THEN 3
            WHEN cs.monetary >= p.monetary_p33  THEN 2
            ELSE 1
        END AS m_score,
        -- Frequency score (3=most orders)
        CASE
            WHEN cs.frequency >= p.freq_p66  THEN 3
            WHEN cs.frequency >= p.freq_p33  THEN 2
            ELSE 1
        END AS f_score,
        -- Recency score (3=most recent — LOWER recency_days = more recent)
        CASE
            WHEN cs.recency_days <= p.recency_p33  THEN 3
            WHEN cs.recency_days <= p.recency_p66  THEN 2
            ELSE 1
        END AS r_score
    FROM customer_stats AS cs
    CROSS JOIN percentiles AS p
),

segmented AS (
    SELECT
        *,
        (r_score + f_score + m_score) AS rfm_total_score,
        CASE
            WHEN r_score = 3 AND f_score = 3 AND m_score = 3 THEN 'Champions'
            WHEN r_score >= 2 AND f_score >= 2 AND m_score >= 2 THEN 'Loyal Customers'
            WHEN r_score = 3 AND f_score <= 2                  THEN 'Recent Customers'
            WHEN r_score >= 2 AND m_score = 3                  THEN 'Big Spenders'
            WHEN r_score = 1 AND f_score >= 2 AND m_score >= 2 THEN 'At Risk'
            WHEN r_score = 1 AND f_score = 1 AND m_score >= 2  THEN 'Lost High Value'
            ELSE                                                     'Needs Attention'
        END AS customer_segment
    FROM scored
)

SELECT
    -- ── Customer Attributes ───────────────────────────────────────────────────────
    dc.customer_id,
    dc.company_name,
    dc.contact_name,
    dc.country,
    dc.city,

    -- ── RFM Scores ───────────────────────────────────────────────────────────────
    sg.r_score,
    sg.f_score,
    sg.m_score,
    sg.rfm_total_score,
    sg.customer_segment,

    -- ── Activity ─────────────────────────────────────────────────────────────────
    sg.recency_days,
    sg.frequency                    AS total_orders,
    sg.active_months,
    sg.first_order_date,
    sg.last_order_date,

    -- ── Revenue ───────────────────────────────────────────────────────────────────
    ROUND(sg.monetary::NUMERIC, 2)  AS total_net_revenue,
    sg.avg_order_value,
    sg.avg_line_value,
    sg.avg_discount_rate,

    -- ── Breadth ───────────────────────────────────────────────────────────────────
    sg.unique_products,
    sg.unique_categories

FROM segmented AS sg
JOIN {{ ref('dim_customers') }} AS dc ON sg.customer_id = dc.customer_id
