SELECT
    -- ── Identity ──────────────────────────────────────────────────────────────────
    shipper_id,
    company_name,
    phone,

    -- ── Surrogate Key ─────────────────────────────────────────────────────────────
    {{ dbt_utils.generate_surrogate_key(['shipper_id']) }} AS dim_shippers_sk

FROM {{ ref('shippers') }}