-- Singular test: every order line in fact_sales must reference a valid order_date
-- in dim_date. If this fails, the date spine in dim_date needs to be extended.

SELECT
    fs.order_id,
    fs.product_id,
    fs.order_date_id
FROM {{ ref('fact_sales') }} AS fs
LEFT JOIN {{ ref('dim_date') }} AS dd
    ON fs.order_date_id = dd.date_id
WHERE fs.order_date_id IS NOT NULL
  AND dd.date_id IS NULL
