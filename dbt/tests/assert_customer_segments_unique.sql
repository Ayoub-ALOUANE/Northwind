-- Singular test: validates that the mart_customer_segments model
-- assigns every possible customer exactly one segment — no customer
-- should appear in more than one segment row.

SELECT
    customer_id,
    COUNT(*) AS segment_row_count
FROM {{ ref('mart_customer_segments') }}
GROUP BY customer_id
HAVING COUNT(*) > 1
