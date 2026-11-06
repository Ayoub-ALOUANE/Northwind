SELECT
    -- ── Identity ──────────────────────────────────────────────────────────────────
    su.supplier_id,
    su.company_name,
    su.contact_name,
    su.contact_title,

    -- ── Location ──────────────────────────────────────────────────────────────────
    su.address,
    su.city,
    su.region,
    su.postal_code,
    su.country,

    -- ── Contact ───────────────────────────────────────────────────────────────────
    su.phone,
    su.fax,
    su.homepage,

    -- ── Derived Supply Metrics ────────────────────────────────────────────────────
    COUNT(pr.product_id)                                        AS total_products_supplied,
    COUNT(CASE WHEN pr.discontinued = FALSE THEN 1 END)         AS active_products_supplied,
    COUNT(CASE WHEN pr.discontinued = TRUE  THEN 1 END)         AS discontinued_products,
    ROUND(AVG(pr.unit_price)::NUMERIC, 2)                       AS avg_product_price,
    ROUND(MIN(pr.unit_price)::NUMERIC, 2)                       AS min_product_price,
    ROUND(MAX(pr.unit_price)::NUMERIC, 2)                       AS max_product_price,

    -- ── Surrogate Key ─────────────────────────────────────────────────────────────
    {{ dbt_utils.generate_surrogate_key(['su.supplier_id']) }}  AS dim_suppliers_sk

FROM {{ ref('suppliers') }} AS su
LEFT JOIN {{ ref('products') }}  AS pr ON su.supplier_id = pr.supplier_id

GROUP BY
    su.supplier_id, su.company_name, su.contact_name, su.contact_title,
    su.address, su.city, su.region, su.postal_code, su.country,
    su.phone, su.fax, su.homepage
