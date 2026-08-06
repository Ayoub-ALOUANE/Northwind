SELECT
    state_id,
    NULLIF(TRIM(state_abbr), '') AS state_abbr,
    NULLIF(TRIM(state_name), '') AS state_name,
    NULLIF(TRIM(state_region), '') AS state_region

FROM {{ source('bronze', 'us_states') }}

WHERE state_id IS NOT NULL
  AND NULLIF(TRIM(state_name), '') IS NOT NULL