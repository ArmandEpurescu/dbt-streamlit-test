with active_listings as (
    select * from {{ ref('int_active_listings_by_day') }}
),
active_listing_counts as (
    select
        metric_date,
        region,
        property_type,
        count(distinct listing_id) as active_listing_count
    from active_listings
    group by 1, 2, 3
),
lead_counts as (
    select
        c.contact_date as metric_date,
        l.region,
        l.property_type,
        count(distinct c.contact_id) as leads_count
    from {{ ref('stg_contacts') }} c
    join {{ ref('stg_listings') }} l
        on c.listing_id = l.listing_id
    group by 1, 2, 3
),
final as (
    select
        a.metric_date,
        a.region,
        a.property_type,
        a.active_listing_count,
        coalesce(l.leads_count, 0) as leads_count,
        round(coalesce(l.leads_count, 0)::double / nullif(a.active_listing_count, 0), 4) as leads_per_active_listing
    from active_listing_counts a
    left join lead_counts l
        on  a.metric_date = l.metric_date
        and a.region = l.region
        and a.property_type = l.property_type
)
select * from final
order by metric_date, region, property_type
