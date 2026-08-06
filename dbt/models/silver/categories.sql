SELECT
    category_id,
    NULLIF(TRIM(category_name), '') AS category_name,
    NULLIF(TRIM(description), '') AS description,
    picture

FROM {{ source('bronze', 'categories') }}

WHERE category_id IS NOT NULL
  AND NULLIF(TRIM(category_name), '') IS NOT NULL