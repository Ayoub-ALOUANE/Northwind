SELECT
    supplier_id,

    NULLIF(TRIM(company_name), '') AS company_name,
    NULLIF(TRIM(contact_name), '') AS contact_name,
    NULLIF(TRIM(contact_title), '') AS contact_title,

    NULLIF(TRIM(address), '') AS address,
    NULLIF(TRIM(city), '') AS city,
    NULLIF(TRIM(region), '') AS region,
    NULLIF(TRIM(postal_code), '') AS postal_code,
    NULLIF(TRIM(country), '') AS country,

    NULLIF(TRIM(phone), '') AS phone,
    NULLIF(TRIM(fax), '') AS fax,
    NULLIF(TRIM(homepage), '') AS homepage

FROM {{ source('bronze', 'suppliers') }}

WHERE supplier_id IS NOT NULL
  AND NULLIF(TRIM(company_name), '') IS NOT NULL