SELECT
    order_id,

    TRIM(customer_id) AS customer_id,
    employee_id,

    order_date,
    required_date,
    shipped_date,

    ship_via,
    freight,

    TRIM(ship_name) AS ship_name,
    TRIM(ship_address) AS ship_address,
    TRIM(ship_city) AS ship_city,
    NULLIF(TRIM(ship_region), '') AS ship_region,
    TRIM(ship_postal_code) AS ship_postal_code,
    TRIM(ship_country) AS ship_country,

    _airbyte_extracted_at AS loaded_at

FROM {{ source('bronze', 'orders') }}