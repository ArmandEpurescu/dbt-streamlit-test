with source as (
    select
        contact_id,
        listing_id,
        contact_source,
        contact_timestamp
    from {{ ref('contacts') }}
),
renamed as (
    select
        trim(cast(contact_id as varchar)) as contact_id,
        trim(cast(listing_id as varchar)) as listing_id,
        lower(trim(cast(contact_source as varchar))) as contact_source,
        cast(contact_timestamp as timestamp) as contact_timestamp,
        cast(contact_timestamp as date) as contact_date
    from source
)
select
    contact_id,
    listing_id,
    contact_source,
    contact_timestamp,
    contact_date
from renamed
