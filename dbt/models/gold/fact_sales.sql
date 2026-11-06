SELECT
    -- ── Natural Keys ────────────────────────────────────────────────────────────
    od.order_id,
    od.product_id,

    -- ── Foreign Keys (dimension links) ──────────────────────────────────────────
    o.customer_id,
    o.employee_id,
    o.ship_via                                  AS shipper_id,
    o.order_date                                AS order_date_id,
    o.required_date                             AS required_date_id,
    o.shipped_date                              AS shipped_date_id,

    -- ── Raw Measures ────────────────────────────────────────────────────────────
    od.quantity,
    od.unit_price,
    od.discount,
    o.freight,

    -- ── Derived Revenue Metrics ──────────────────────────────────────────────────
    ROUND((od.quantity * od.unit_price)::NUMERIC, 2)                    AS gross_revenue,
    ROUND((od.quantity * od.unit_price * (1 - od.discount))::NUMERIC, 2) AS net_revenue,
    ROUND((od.quantity * od.unit_price * od.discount)::NUMERIC, 2)      AS discount_amount,

    -- ── Discount Tier ───────────────────────────────────────────────────────────
    CASE
        WHEN od.discount = 0             THEN 'No Discount'
        WHEN od.discount <= 0.05         THEN 'Light (1-5%)'
        WHEN od.discount <= 0.15         THEN 'Moderate (6-15%)'
        ELSE                                  'Heavy (16%+)'
    END                                                                 AS discount_tier,

    -- ── Shipping Performance ─────────────────────────────────────────────────────
    CASE
        WHEN o.shipped_date IS NULL              THEN NULL
        WHEN o.shipped_date > o.required_date    THEN TRUE
        ELSE                                          FALSE
    END                                                                 AS is_late_shipment,

    CASE
        WHEN o.shipped_date IS NULL THEN NULL
        ELSE (o.shipped_date::DATE - o.order_date::DATE)
    END                                                                 AS days_to_ship,

    CASE
        WHEN o.shipped_date IS NULL THEN NULL
        ELSE (o.required_date::DATE - o.shipped_date::DATE)
    END                                                                 AS days_early_or_late, -- positive = early, negative = late

    -- ── Destination ──────────────────────────────────────────────────────────────
    o.ship_country,
    o.ship_city,

    -- ── Surrogate Key ────────────────────────────────────────────────────────────
    {{ dbt_utils.generate_surrogate_key(['od.order_id', 'od.product_id']) }} AS fact_sales_sk

FROM {{ ref('order_details') }} AS od
LEFT JOIN {{ ref('orders') }} AS o
    ON od.order_id = o.order_id
