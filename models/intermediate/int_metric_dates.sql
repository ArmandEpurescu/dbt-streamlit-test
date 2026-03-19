with bounds as (
    select
        least(
            min(created_at),
            (select min(contact_date) from {{ ref('stg_contacts') }})
        ) as min_metric_date,
        greatest(
            max(updated_at),
            (select max(contact_date) from {{ ref('stg_contacts') }})
        ) as max_metric_date
    from {{ ref('stg_listings') }}
),
spine as (
    select cast(metric_date as date) as metric_date
    from bounds,
    generate_series(min_metric_date, max_metric_date, interval 1 day) as t(metric_date)
)
select * from spine
