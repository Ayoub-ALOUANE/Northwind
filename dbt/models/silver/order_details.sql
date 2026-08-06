SELECT
    order_id,
    product_id,
    unit_price,
    quantity,
    discount

FROM {{ source('bronze', 'order_details') }}

WHERE order_id IS NOT NULL
  AND product_id IS NOT NULL
  AND quantity > 0
  AND unit_price >= 0
  AND discount BETWEEN 0 AND 1