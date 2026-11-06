SELECT
    -- ── Identity ──────────────────────────────────────────────────────────────────
    customer_id,
    company_name,
    contact_name,
    contact_title,

    -- ── Location ──────────────────────────────────────────────────────────────────
    address,
    city,
    region,
    postal_code,
    country,

    -- ── Contact ───────────────────────────────────────────────────────────────────
    phone,
    fax,

    -- ── Surrogate Key ─────────────────────────────────────────────────────────────
    {{ dbt_utils.generate_surrogate_key(['customer_id']) }} AS dim_customers_sk

FROM {{ ref('customers') }}
