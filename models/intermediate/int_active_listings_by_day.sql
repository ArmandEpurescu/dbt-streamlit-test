with metric_dates as (
    select * from {{ ref('int_metric_dates') }}
),
listings as (
    select * from {{ ref('stg_listings') }}
)
select
    d.metric_date,
    l.listing_id,
    l.property_type,
    l.region
from metric_dates d
join listings l
    on {{ is_active_listing('d.metric_date', 'l.created_at', 'l.updated_at') }}