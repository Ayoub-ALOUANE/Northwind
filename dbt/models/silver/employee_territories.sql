SELECT
    employee_id,
    TRIM(territory_id) AS territory_id,
    _airbyte_extracted_at AS loaded_at
FROM {{ source('bronze', 'employee_territories') }}
WHERE
    employee_id IS NOT NULL
    AND territory_id IS NOT NULL