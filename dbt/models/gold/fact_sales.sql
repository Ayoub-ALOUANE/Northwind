SELECT
    od.order_id,
    od.product_id,
    od.quantity,
    od.unit_price,
    od.discount,

    o.customer_id,
    o.employee_id,
    o.ship_via AS shipper_id,
    o.order_date AS order_date_id,
    o.required_date AS required_date_id,
    o.shipped_date AS shipped_date_id

FROM {{ ref('order_details') }} AS od
LEFT JOIN {{ ref('orders') }} AS o
    ON od.order_id = o.order_id