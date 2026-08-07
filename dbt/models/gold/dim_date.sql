WITH dates AS (
    SELECT
        GENERATE_SERIES(
            DATE '1996-01-01',
            DATE '1998-12-31',
            INTERVAL '1 day'
        ) AS date_day
)

SELECT
    date_day AS date_id,
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(QUARTER FROM date_day) AS quarter,
    EXTRACT(MONTH FROM date_day) AS month,
    TRIM(TO_CHAR(date_day, 'Month')) AS month_name,
    EXTRACT(DAY FROM date_day) AS day,
    TRIM(TO_CHAR(date_day, 'Day')) AS day_name

FROM dates