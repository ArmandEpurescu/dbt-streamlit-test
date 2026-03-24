{% snapshot snap_listings %}

{{
    config(
      target_schema='snapshots',
      unique_key='listing_id',
      strategy='check',
      check_cols=['property_type', 'city', 'region', 'price', 'updated_at']
    )
}}

select
    listing_id,
    property_type,
    city,
    region,
    price,
    created_at,
    updated_at,
    agent_id
from {{ ref('stg_listings') }}

{% endsnapshot %}
