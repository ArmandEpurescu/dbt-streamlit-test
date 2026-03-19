-- Example: latest 14-day average lead density by region/property type
select
    region,
    property_type,
    round(avg(leads_per_active_listing), 4) as avg_leads_per_active_listing_last_14d
from {{ ref('mart_leads_per_active_listing') }}
where metric_date >= (select max(metric_date) - interval 13 day from {{ ref('mart_leads_per_active_listing') }})
group by 1, 2
order by 3 desc, 1, 2
