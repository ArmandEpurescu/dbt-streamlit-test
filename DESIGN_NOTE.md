# Design Note - AVIV Data Platform & Analytics Engineering Case

## Objective
Build a compact, trustworthy analytics pipeline that turns raw property listings and leads into a business-ready dataset with dbt.

## Architecture choice
For the submission, I used **local CSVs + DuckDB + dbt** so the project runs end-to-end without cloud dependencies. That fits the brief, which explicitly allows **S3 or local CSVs** and says it is fine to **simplify or simulate** setup.

In production, the same modeling pattern would run on **AWS / S3 -> Snowflake -> dbt**.

## Modeling approach
I used three layers:
- **Seeds / raw demo inputs:** generated CSVs for listings and contacts
- **Staging:** datatype cleanup, string normalization, and enum standardization
- **Mart:** `mart_leads_per_active_listing`, grouped by `metric_date`, `region`, and `property_type`

## Metric definition
Because there is no explicit listing status, I defined an **active listing** as:
- created on or before the metric date, and
- updated within the previous 30 days.

This is simple, defensible, and easy to replace later if a true lifecycle status becomes available.

## Data quality controls
1. **Uniqueness + not null** on `listing_id` and `contact_id`  
   Prevents duplicate counting and broken joins.
2. **Relationships** from contacts to listings  
   Ensures every reported lead belongs to a valid listing.
3. **Accepted values** for `property_type` and `contact_source`  
   Protects dimensions from taxonomy drift.

## Real-world considerations
- **Schema drift:** land permissively, then promote new columns intentionally in staging.
- **Slowly changing attributes:** snapshot price / region changes for historical analysis; overwrite for current-state marts.
- **Late-arriving leads:** backfill a recent window so delayed events update past dates.
- **Data contracts:** require keys, timestamps, mandatory columns, controlled enums, and file-delivery SLAs.
- **Performance vs cost:** table for repeated BI usage; incremental table at scale.

## Business takeaway
In the mock dataset, **apartments in Ile-de-France** show the strongest recent lead density, while parking inventory is weaker. Even with tiny demo data, the mart surfaces where demand is strongest relative to available supply.

## Productionization
To move this into the AVIV stack, I would land files in S3, ingest them to Snowflake via `COPY INTO` or Snowpipe, orchestrate dbt, add freshness / volume monitoring, and expose the mart to BI.
