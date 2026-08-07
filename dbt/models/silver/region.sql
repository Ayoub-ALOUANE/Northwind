SELECT
    region_id,
    NULLIF(TRIM(region_description), '') AS region_description,

    _airbyte_extracted_at AS loaded_at

FROM {{ source('bronze', 'region') }}

WHERE region_id IS NOT NULL
  AND NULLIF(TRIM(region_description), '') IS NOT NULL