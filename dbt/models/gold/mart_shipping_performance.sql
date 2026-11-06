{{
    config(
        materialized = 'table',
        schema       = 'gold'
    )
}}

-- ─────────────────────────────────────────────────────────────────────────────
-- mart_shipping_performance
-- Grain: one row per shipper per month
-- Purpose: monitors carrier performance over time — late rates, avg delivery
--          speed, revenue moved, and freight costs. Drives logistics dashboards.
-- ─────────────────────────────────────────────────────────────────────────────

WITH shipments AS (
    SELECT
        fs.shipper_id,
        fs.order_date_id,
        dd.year,
        dd.month,
        dd.month_name,
        dd.year_month,
        fs.order_id,
        fs.net_revenue,
        fs.freight,
        fs.is_late_shipment,
        fs.days_to_ship,
        fs.days_early_or_late,
        fs.ship_country
    FROM {{ ref('fact_sales') }} AS fs
    LEFT JOIN {{ ref('dim_date') }} AS dd ON fs.order_date_id = dd.date_id
    WHERE fs.shipped_date_id IS NOT NULL   -- only completed shipments
)

SELECT
    -- ── Shipper Info ──────────────────────────────────────────────────────────────
    ds.shipper_id,
    ds.company_name                                     AS shipper_name,
    ds.phone                                            AS shipper_phone,

    -- ── Time Grain ───────────────────────────────────────────────────────────────
    sh.year,
    sh.month,
    sh.month_name,
    sh.year_month,

    -- ── Volume ───────────────────────────────────────────────────────────────────
    COUNT(DISTINCT sh.order_id)                         AS total_shipments,
    COUNT(DISTINCT sh.ship_country)                     AS countries_served,

    -- ── Revenue Carried ───────────────────────────────────────────────────────────
    ROUND(SUM(sh.net_revenue)::NUMERIC, 2)              AS total_revenue_shipped,
    ROUND(SUM(sh.freight)::NUMERIC, 2)                  AS total_freight_charged,

    -- ── Performance ───────────────────────────────────────────────────────────────
    SUM(CASE WHEN sh.is_late_shipment = TRUE  THEN 1 ELSE 0 END) AS late_shipments,
    SUM(CASE WHEN sh.is_late_shipment = FALSE THEN 1 ELSE 0 END) AS on_time_shipments,
    ROUND(
        SUM(CASE WHEN sh.is_late_shipment = TRUE THEN 1 ELSE 0 END)::NUMERIC
        / NULLIF(COUNT(DISTINCT sh.order_id), 0) * 100
    , 1)                                                AS late_shipment_rate_pct,
    ROUND(AVG(sh.days_to_ship)::NUMERIC, 1)             AS avg_days_to_ship,
    ROUND(AVG(sh.days_early_or_late)::NUMERIC, 1)       AS avg_days_early_or_late, -- negative = avg late
    MIN(sh.days_to_ship)                                AS min_days_to_ship,
    MAX(sh.days_to_ship)                                AS max_days_to_ship

FROM shipments AS sh
JOIN {{ ref('dim_shippers') }} AS ds ON sh.shipper_id = ds.shipper_id
GROUP BY
    ds.shipper_id, ds.company_name, ds.phone,
    sh.year, sh.month, sh.month_name, sh.year_month
