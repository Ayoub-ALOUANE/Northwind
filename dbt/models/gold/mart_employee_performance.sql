{{
    config(
        materialized = 'table',
        schema       = 'gold'
    )
}}

-- ─────────────────────────────────────────────────────────────────────────────
-- mart_employee_performance
-- Grain: one row per employee
-- Purpose: aggregates sales performance, territory coverage, and shipping
--          KPIs per employee — for HR reviews, territory planning, and
--          sales management dashboards.
-- ─────────────────────────────────────────────────────────────────────────────

WITH employee_sales AS (
    SELECT
        fs.employee_id,
        COUNT(DISTINCT fs.order_id)                              AS total_orders,
        COUNT(*)                                                 AS total_order_lines,
        COUNT(DISTINCT fs.customer_id)                           AS unique_customers_served,
        COUNT(DISTINCT fs.product_id)                            AS unique_products_sold,
        SUM(fs.quantity)                                         AS total_units_sold,
        ROUND(SUM(fs.gross_revenue)::NUMERIC, 2)                 AS total_gross_revenue,
        ROUND(SUM(fs.net_revenue)::NUMERIC, 2)                   AS total_net_revenue,
        ROUND(SUM(fs.discount_amount)::NUMERIC, 2)               AS total_discount_given,
        ROUND(AVG(fs.discount)::NUMERIC, 4)                      AS avg_discount_rate,
        ROUND(
            SUM(fs.net_revenue) / NULLIF(COUNT(DISTINCT fs.order_id), 0)
        ::NUMERIC, 2)                                            AS avg_order_value,
        SUM(CASE WHEN fs.is_late_shipment = TRUE  THEN 1 ELSE 0 END) AS late_shipments,
        SUM(CASE WHEN fs.is_late_shipment = FALSE THEN 1 ELSE 0 END) AS on_time_shipments,
        ROUND(AVG(CASE WHEN fs.days_to_ship IS NOT NULL THEN fs.days_to_ship END)::NUMERIC, 1)
                                                                 AS avg_days_to_ship,
        MIN(fs.order_date_id)                                    AS first_order_date,
        MAX(fs.order_date_id)                                    AS last_order_date,
        COUNT(DISTINCT DATE_TRUNC('month', fs.order_date_id::DATE)) AS active_months
    FROM {{ ref('fact_sales') }} AS fs
    GROUP BY fs.employee_id
),

territory_counts AS (
    SELECT
        employee_id,
        COUNT(*)                  AS territory_count,
        {% if target.type == 'snowflake' %}
        LISTAGG(region_description, ', ') WITHIN GROUP (ORDER BY region_description) AS regions_covered
        {% else %}
        STRING_AGG(region_description, ', ' ORDER BY region_description) AS regions_covered
        {% endif %}
    FROM {{ ref('bridge_employee_territories') }}
    GROUP BY employee_id
)

SELECT
    -- ── Employee Attributes ───────────────────────────────────────────────────────
    de.employee_id,
    de.full_name,
    de.title,
    de.title_of_courtesy,
    de.hire_date,
    de.years_of_service,
    de.country,
    de.city,
    de.manager_full_name,
    de.manager_title,

    -- ── Territory Coverage ────────────────────────────────────────────────────────
    COALESCE(tc.territory_count, 0)     AS territory_count,
    tc.regions_covered,

    -- ── Sales Volume ──────────────────────────────────────────────────────────────
    COALESCE(es.total_orders, 0)        AS total_orders,
    COALESCE(es.total_order_lines, 0)   AS total_order_lines,
    COALESCE(es.unique_customers_served, 0) AS unique_customers_served,
    COALESCE(es.unique_products_sold, 0)    AS unique_products_sold,
    COALESCE(es.total_units_sold, 0)    AS total_units_sold,
    COALESCE(es.active_months, 0)       AS active_months,

    -- ── Revenue ───────────────────────────────────────────────────────────────────
    COALESCE(es.total_gross_revenue, 0) AS total_gross_revenue,
    COALESCE(es.total_net_revenue, 0)   AS total_net_revenue,
    COALESCE(es.total_discount_given, 0) AS total_discount_given,
    es.avg_discount_rate,
    es.avg_order_value,

    -- ── Monthly Run Rate ──────────────────────────────────────────────────────────
    ROUND(
        es.total_net_revenue::NUMERIC / NULLIF(es.active_months, 0)
    , 2)                                AS avg_monthly_revenue,

    -- ── Shipping Performance ──────────────────────────────────────────────────────
    COALESCE(es.late_shipments, 0)      AS late_shipments,
    COALESCE(es.on_time_shipments, 0)   AS on_time_shipments,
    ROUND(
        es.late_shipments::NUMERIC
        / NULLIF(es.late_shipments + es.on_time_shipments, 0) * 100
    , 1)                                AS late_shipment_rate_pct,
    es.avg_days_to_ship,

    -- ── Timeline ──────────────────────────────────────────────────────────────────
    es.first_order_date,
    es.last_order_date

FROM {{ ref('dim_employees') }}            AS de
LEFT JOIN employee_sales                   AS es ON de.employee_id = es.employee_id
LEFT JOIN territory_counts                 AS tc ON de.employee_id = tc.employee_id
