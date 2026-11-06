-- ─────────────────────────────────────────────────────────────────────────────
-- financial.sql — Reusable financial calculation macros
-- ─────────────────────────────────────────────────────────────────────────────

{% macro safe_divide(numerator, denominator) %}
    CASE
        WHEN {{ denominator }} = 0 OR {{ denominator }} IS NULL THEN NULL
        ELSE {{ numerator }}::NUMERIC / {{ denominator }}::NUMERIC
    END
{% endmacro %}


{% macro gross_revenue(quantity, unit_price) %}
    ROUND(({{ quantity }} * {{ unit_price }})::NUMERIC, 2)
{% endmacro %}


{% macro net_revenue(quantity, unit_price, discount) %}
    ROUND(({{ quantity }} * {{ unit_price }} * (1 - {{ discount }}))::NUMERIC, 2)
{% endmacro %}


{% macro discount_amount(quantity, unit_price, discount) %}
    ROUND(({{ quantity }} * {{ unit_price }} * {{ discount }})::NUMERIC, 2)
{% endmacro %}


{% macro discount_tier(discount_col) %}
    CASE
        WHEN {{ discount_col }} = 0      THEN 'No Discount'
        WHEN {{ discount_col }} <= 0.05  THEN 'Light (1-5%)'
        WHEN {{ discount_col }} <= 0.15  THEN 'Moderate (6-15%)'
        ELSE                                  'Heavy (16%+)'
    END
{% endmacro %}
