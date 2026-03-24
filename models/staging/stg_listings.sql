with source as (
    select * from {{ ref('listings') }}
),
renamed as (
    select
        trim(cast(listing_id as varchar)) as listing_id,
        lower(trim(cast(property_type as varchar))) as property_type,
        trim(cast(city as varchar)) as city,
        trim(cast(region as varchar)) as region,
        cast(price as bigint) as price,
        cast(created_at as date) as created_at,
        cast(updated_at as date) as updated_at,
        trim(cast(agent_id as varchar)) as agent_id
    from source
)
select
    listing_id,
    property_type,
    city,
    region,
    price,
    created_at,
    updated_at,
    agent_id
from renamed
