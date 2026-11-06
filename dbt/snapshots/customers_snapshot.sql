{% snapshot customers_snapshot %}

{{
    config(
        target_schema = 'snapshots',
        unique_key    = 'customer_id',
        strategy      = 'check',
        check_cols    = ['company_name', 'contact_name', 'contact_title',
                         'address', 'city', 'region', 'postal_code', 'country',
                         'phone', 'fax']
    )
}}

SELECT
    customer_id,
    company_name,
    contact_name,
    contact_title,
    address,
    city,
    region,
    postal_code,
    country,
    phone,
    fax
FROM {{ source('bronze', 'customers') }}

{% endsnapshot %}
