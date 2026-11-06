-- ─────────────────────────────────────────────────────────────────────────────
-- Generic custom test: assert_column_is_between
-- Generic custom test: assert_not_empty
--
-- These are generic (parametric) tests that can be applied in schema.yml
-- to any model/column combination without writing new SQL each time.
-- ─────────────────────────────────────────────────────────────────────────────


-- ── assert_column_is_between ──────────────────────────────────────────────────
-- Usage in schema.yml:
--   columns:
--     - name: discount
--       tests:
--         - assert_column_is_between:
--             min_value: 0
--             max_value: 1
--
-- Returns rows that violate the [min_value, max_value] range. Test fails if any rows returned.

{% test assert_column_is_between(model, column_name, min_value, max_value) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND ({{ column_name }} < {{ min_value }} OR {{ column_name }} > {{ max_value }})

{% endtest %}


-- ── assert_not_empty ─────────────────────────────────────────────────────────
-- Usage in schema.yml:
--   models:
--     - name: fact_sales
--       tests:
--         - assert_not_empty:
--             column_name: order_id
--
-- Fails if the model has zero rows. Guards against empty table after bad sync.

{% test assert_not_empty(model, column_name) %}

SELECT 1
WHERE NOT EXISTS (
    SELECT 1
    FROM {{ model }}
    LIMIT 1
)

{% endtest %}
