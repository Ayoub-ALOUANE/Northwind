SELECT
    TRIM(customer_id)   AS customer_id,
    TRIM(company_name)  AS company_name,
    TRIM(contact_name)  AS contact_name,
    TRIM(contact_title) AS contact_title,
    TRIM(address)       AS address,
    TRIM(city)          AS city,
    TRIM(region)        AS region,
    TRIM(postal_code)   AS postal_code,
    TRIM(country)       AS country,
    TRIM(phone)         AS phone,
    TRIM(fax)           AS fax

FROM {{ source('bronze', 'customers') }}

WHERE NULLIF(TRIM(customer_id), '') IS NOT NULL
  AND NULLIF(TRIM(company_name), '') IS NOT NULL