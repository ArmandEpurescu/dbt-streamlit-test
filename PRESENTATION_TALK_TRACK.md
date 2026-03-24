# 5-minute talk track (English)

## 1) Challenge & framing
- I treated the case as a miniature SeLoger pipeline: daily listings/leads landing in S3 or CSV, modeled with dbt, measured via Snowflake/AWS in production but runnable locally (CSV ➜ DuckDB ➜ dbt) for demo purposes.
- Goal: prove I can turn raw operational data into a trustworthy KPI plus explain the operational trade-offs the panel asked about (schema drift, data contracts, late leads, cost vs. performance).

## 2) Ingestion & data contracts
- Production path: S3 prefixes like `s3://seloger-data-prod/listings/2026-03-25/` feed external Snowflake stages. A Dagster job issues `COPY INTO raw.listings` or we enable Snowpipe with auto-ingest.
- Minimal data contract enforced before Snowflake: Lambda validates schema, row counts, control files, timestamps, and enum adherence; we only invoke COPY/Snowpipe when checks succeed.
- IaC manages stages, file formats, pipes so that schema changes are reviewed; README documents both COPY and Snowpipe options plus validation hooks.

## 3) Modeling & data quality (dbt requirements)
- Staging models (`stg_listings`, `stg_contacts`) explicitly select/clean every column, normalize enums, and cast dates—no `select *`.
- Intermediate layer builds `int_metric_dates` (date spine) and `int_active_listings_by_day` (30-day freshness window) because we lack an explicit status flag. Mart `mart_leads_per_active_listing` aggregates by date/region/property type.
- Tests: uniqueness & not-null on IDs, relationships contacts→listings, accepted values for property_type/contact_source. These mitigate duplicate KPIs, orphan leads, and taxonomy drift.

## 4) Business insight emphasis
- KPI: Leads per Active Listing. Latest 14-day readout shows Île-de-France apartments at 0.60 (priority inventory), Provence-Alpes-Côte d'Azur houses trending up at 0.36, Occitanie apartments volatile at 0.21, and parking essentially zero.
- `analyses/business_metric_insights.md` translates numbers into actions (double down on high-performing regions, stabilize Occitanie visibility, rethink parking monetization).
- This answers the brief’s “show business value” ask by highlighting where marketing/sales should allocate focus immediately.

## 5) Operations, CI/CD & next steps
- GitHub Actions workflow (`dbt-ci.yml`) runs `dbt deps/seed/run/test` on every push/PR to keep quality gates automated.
- Productionization playbook: incremental materializations for large staging/intermediate tables, table mart for BI, snapshot for slowly changing attributes, backfill last 14 days to capture late leads, freshness/volume monitoring layered on top.
- Next iterations: wire up Snowflake connectivity, add observability (Elementary/dbt metrics), and expose mart via Streamlit dashboard pointed at Snowflake.
