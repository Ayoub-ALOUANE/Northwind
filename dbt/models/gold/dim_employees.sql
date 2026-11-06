SELECT
    -- ── Identity ──────────────────────────────────────────────────────────────────
    e.employee_id,
    e.first_name,
    e.last_name,
    e.first_name || ' ' || e.last_name          AS full_name,
    e.title,
    e.title_of_courtesy,

    -- ── Dates ─────────────────────────────────────────────────────────────────────
    e.birth_date,
    e.hire_date,
    {% if target.type == 'snowflake' %}
    DATEDIFF('year', e.hire_date::DATE, CURRENT_DATE()) AS years_of_service,
    {% else %}
    DATE_PART('year', AGE(e.hire_date::DATE))           AS years_of_service,
    {% endif %}

    -- ── Location ──────────────────────────────────────────────────────────────────
    e.address,
    e.city,
    e.region,
    e.postal_code,
    e.country,

    -- ── Contact ───────────────────────────────────────────────────────────────────
    e.home_phone,
    e.extension,

    -- ── Reporting ─────────────────────────────────────────────────────────────────
    e.reports_to,
    mgr.first_name || ' ' || mgr.last_name       AS manager_full_name,
    mgr.title                                    AS manager_title,

    -- ── Notes ─────────────────────────────────────────────────────────────────────
    e.notes,

    -- ── Surrogate Key ─────────────────────────────────────────────────────────────
    {{ dbt_utils.generate_surrogate_key(['e.employee_id']) }} AS dim_employees_sk

FROM {{ ref('employees') }} AS e
LEFT JOIN {{ ref('employees') }} AS mgr
    ON e.reports_to = mgr.employee_id