SELECT
    employee_id,

    NULLIF(TRIM(first_name), '') AS first_name,
    NULLIF(TRIM(last_name), '') AS last_name,
    NULLIF(TRIM(title), '') AS title,
    NULLIF(TRIM(title_of_courtesy), '') AS title_of_courtesy,

    birth_date,
    hire_date,

    NULLIF(TRIM(address), '') AS address,
    NULLIF(TRIM(city), '') AS city,
    NULLIF(TRIM(region), '') AS region,
    NULLIF(TRIM(postal_code), '') AS postal_code,
    NULLIF(TRIM(country), '') AS country,

    NULLIF(TRIM(home_phone), '') AS home_phone,
    NULLIF(TRIM(extension), '') AS extension,

    NULLIF(TRIM(photo), '') AS photo,
    NULLIF(TRIM(photo_path), '') AS photo_path,

    NULLIF(TRIM(notes), '') AS notes,

    reports_to,

    _airbyte_extracted_at AS loaded_at

FROM {{ source('bronze', 'employees') }}

WHERE employee_id IS NOT NULL