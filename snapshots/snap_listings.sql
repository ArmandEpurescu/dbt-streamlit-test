{% snapshot snap_listings %}

{{
    config(
      target_schema='snapshots',
      unique_key='listing_id',
      strategy='check',
      check_cols=['property_type', 'city', 'region', 'price', 'updated_at']
    )
}}

select * from {{ ref('stg_listings') }}

{% endsnapshot %}
