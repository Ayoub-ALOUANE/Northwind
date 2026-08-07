SELECT
    empt.employee_id,
    empt.territory_id,

    te.territory_description,

    re.region_id,
    re.region_description
    
FROM {{ ref('employee_territories') }} as empt
LEFT JOIN {{ ref('territories') }} AS te
    ON empt.territory_id = te.territory_id
LEFT JOIN {{ ref('region') }} AS re
    ON te.region_id = re.region_id
