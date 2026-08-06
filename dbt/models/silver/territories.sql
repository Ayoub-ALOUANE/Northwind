SELECT
    NULLIF(TRIM(territory_id), '') AS territory_id,
    NULLIF(TRIM(territory_description), '') AS territory_description,
    region_id

FROM {{ source('bronze', 'territories') }}

WHERE NULLIF(TRIM(territory_id), '') IS NOT NULL
  AND region_id IS NOT NULL