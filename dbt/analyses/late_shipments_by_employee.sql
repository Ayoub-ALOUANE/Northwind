-- Late shipments by employee — measures on-time delivery performance per sales rep.
-- A high late_shipment_rate may indicate territory overload or carrier issues.

SELECT
    de.employee_id,
    de.full_name,
    de.title,
    de.manager_full_name,

    COUNT(*)                                                     AS total_order_lines,
    COUNT(DISTINCT fs.order_id)                                  AS total_orders,
    SUM(CASE WHEN fs.is_late_shipment = TRUE THEN 1 ELSE 0 END)  AS late_shipments,
    ROUND(
        SUM(CASE WHEN fs.is_late_shipment = TRUE THEN 1 ELSE 0 END)::NUMERIC
        / NULLIF(COUNT(CASE WHEN fs.is_late_shipment IS NOT NULL THEN 1 END), 0) * 100
    , 1)                                                         AS late_shipment_rate_pct,

    ROUND(AVG(CASE WHEN fs.days_to_ship IS NOT NULL THEN fs.days_to_ship END)::NUMERIC, 1)
                                                                 AS avg_days_to_ship,
    MAX(fs.days_to_ship)                                         AS max_days_to_ship,
    ROUND(SUM(fs.net_revenue)::NUMERIC, 2)                       AS total_net_revenue

FROM {{ ref('fact_sales') }}    AS fs
JOIN {{ ref('dim_employees') }} AS de ON fs.employee_id = de.employee_id

WHERE fs.shipped_date_id IS NOT NULL   -- only shipped orders
GROUP BY de.employee_id, de.full_name, de.title, de.manager_full_name
ORDER BY late_shipment_rate_pct DESC
