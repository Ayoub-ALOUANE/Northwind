SELECT
    pr.product_id,
    pr.product_name,
    pr.supplier_id,
    pr.category_id,
    pr.quantity_per_unit,
    pr.unit_price,
    pr.units_in_stock,
    pr.units_on_order,
    pr.reorder_level,
    pr.discontinued,

    ca.category_name,

    su.company_name AS supplier_company_name,
    su.city AS supplier_city,
    su.region AS supplier_region,
    su.country AS supplier_country

FROM {{ ref('products') }} AS pr
LEFT JOIN {{ ref('categories') }} AS ca
    ON pr.category_id = ca.category_id
LEFT JOIN {{ ref('suppliers') }} AS su
    ON pr.supplier_id = su.supplier_id