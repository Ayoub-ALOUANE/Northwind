{% if target.type == 'snowflake' %}
WITH dates AS (
    SELECT
        DATEADD(day, SEQ4(), DATE '1996-01-01') AS date_day
    FROM TABLE(GENERATOR(ROWCOUNT => 13000))
)
{% else %}
WITH dates AS (
    SELECT
        GENERATE_SERIES(
            DATE '1996-01-01',
            DATE '2030-12-31',
            INTERVAL '1 day'
        ) AS date_day
)
{% endif %}

SELECT
    -- ── Primary Key ───────────────────────────────────────────────────────────────
    date_day                                        AS date_id,

    -- ── Standard Date Parts ───────────────────────────────────────────────────────
    EXTRACT(YEAR    FROM date_day)::INT             AS year,
    EXTRACT(QUARTER FROM date_day)::INT             AS quarter,
    EXTRACT(MONTH   FROM date_day)::INT             AS month,
    EXTRACT(DAY     FROM date_day)::INT             AS day,

    -- ── Named Periods ─────────────────────────────────────────────────────────────
    TRIM(TO_CHAR(date_day, 'Month'))                AS month_name,
    TRIM(TO_CHAR(date_day, 'Mon'))                  AS month_short,
    'Q' || EXTRACT(QUARTER FROM date_day)::INT      AS quarter_name,

    -- ── Week ──────────────────────────────────────────────────────────────────────
    EXTRACT(WEEK FROM date_day)::INT                AS week_of_year,
    EXTRACT(DOW  FROM date_day)::INT                AS day_of_week_num, -- 0=Sunday
    TRIM(TO_CHAR(date_day, 'Day'))                  AS day_name,
    TRIM(TO_CHAR(date_day, 'Dy'))                   AS day_short,

    -- ── Boolean Flags ─────────────────────────────────────────────────────────────
    EXTRACT(DOW FROM date_day) IN (0, 6)            AS is_weekend,
    EXTRACT(DOW FROM date_day) NOT IN (0, 6)        AS is_weekday,

    -- ── Year-Month Key (useful for grouping) ──────────────────────────────────────
    TO_CHAR(date_day, 'YYYY-MM')                    AS year_month

FROM dates