SELECT
    shipper_id,
    NULLIF(TRIM(company_name), '') AS company_name,
    NULLIF(TRIM(phone), '') AS phone,

    _airbyte_extracted_at AS loaded_at

FROM {{ source('bronze', 'shippers') }}

WHERE shipper_id IS NOT NULL
  AND NULLIF(TRIM(company_name), '') IS NOT NULL