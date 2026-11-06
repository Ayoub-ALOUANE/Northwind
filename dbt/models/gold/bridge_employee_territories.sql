SELECT
    empt.employee_id,
    empt.territory_id,

    te.territory_description,

    re.region_id,
    re.region_description,
    
    {{dbt_utils.generate_surrogate_key(['empt.employee_id', 'empt.territory_id', 're.region_id'])}} bridge_employee_territories_surrogate_key
    
FROM {{ ref('employee_territories') }} as empt
LEFT JOIN {{ ref('territories') }} AS te
    ON empt.territory_id = te.territory_id
LEFT JOIN {{ ref('region') }} AS re
    ON te.region_id = re.region_id
