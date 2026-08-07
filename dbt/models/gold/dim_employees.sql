SELECT
    employee_id,
    first_name,
    last_name,
    title,
    title_of_courtesy,
    birth_date,
    hire_date,
    city,
    region,
    country,
    reports_to


FROM {{ ref('employees') }}