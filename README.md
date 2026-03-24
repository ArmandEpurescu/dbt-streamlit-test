# AVIV Data Platform & Analytics Engineering Case

This repository is an interview-sized solution for the AVIV / SeLoger analytics case.

It is intentionally built as a **local demo** using **CSV seeds + DuckDB + dbt** so it can run end-to-end without a Snowflake account. That matches the brief: data may arrive via **S3 or local CSVs**, and it is fine to **simplify or simulate** parts of the setup. In production, the same modeling layer would sit behind an AWS -> Snowflake -> dbt pipeline.
## What is included

- `sample_data/`: mock CSVs used as dbt seeds
- `models/staging/`: cleaning and normalization models
- `models/intermediate/`: date spine and active-listing logic
- `models/marts/`: business-ready mart for **Leads per Active Listing**
- `snapshots/`: optional Type-2 style snapshot for listing attributes
- `analyses/business_query.sql`: example business query
- `profiles.example.yml`: minimal DuckDB profile example
- `DESIGN_NOTE.*`: 1-2 page write-up for the interview

## Architecture

### Demo / submission architecture
**local CSVs -> dbt seeds -> staging -> mart -> SQL / BI**

### Production architecture
**AWS / S3 landing -> Snowflake raw -> dbt staging -> dbt mart -> BI**

The important point is that the **dbt modeling layer stays the same**. For the case, I simplified the storage/warehouse layer to make the project runnable locally while still documenting how I would ingest into Snowflake in production.

## Business metric

The primary mart is `mart_leads_per_active_listing`.

### Active listing definition used here
A listing is considered **active** on a `metric_date` when:
- `created_at <= metric_date`
- `updated_at >= metric_date - 30 days`

This is a pragmatic proxy because the dataset has no explicit status / deactivation field.

### Metric formula
`leads_per_active_listing = leads_count / active_listing_count`

Dimensions:
- `metric_date`
- `region`
- `property_type`

## Why this submission is aligned with the brief

The case explicitly asks for:
- daily data arriving in **S3 or local CSVs**
- a **dbt staging model** and a **mart model**
- a few **dbt tests**
- a short design note that explains the production path to **Snowflake** and trade-offs. fileciteturn3file0L18-L33 fileciteturn3file1L1-L20

So this repo demonstrates the logic locally, then documents how the same design would be productionized on Snowflake.

## Local run instructions (DuckDB)

### 1. Install dependencies
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install dbt-duckdb
```

### 2. Create a dbt profile
Create `~/.dbt/profiles.yml` with:

```yaml
aviv_case:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: aviv_case.duckdb
      threads: 4
      schema: analytics
```

You can also copy `profiles.example.yml` into `~/.dbt/profiles.yml`.

### 3. Run the project
From the project root:

```bash
dbt seed
dbt snapshot
dbt run
dbt test
dbt docs generate
```

Optional connectivity check:

```bash
dbt debug
```

## Project structure

```text
sample_data/
  listings.csv
  contacts.csv
models/
  staging/
    stg_listings.sql
    stg_contacts.sql
    schema.yml
  intermediate/
    int_metric_dates.sql
    int_active_listings_by_day.sql
  marts/
    mart_leads_per_active_listing.sql
    schema.yml
snapshots/
  snap_listings.sql
analyses/
  business_query.sql
```

## Tests included and why they matter

- **Uniqueness / not null on listing_id and contact_id**  
  Prevents duplicate counting and unstable joins.

- **Relationship from contacts to listings**  
  Ensures every lead belongs to a valid listing and avoids inflated or orphaned KPIs.

- **Accepted values for property_type and contact_source**  
  Protects dimensional consistency and catches taxonomy drift early.

## Production path to Snowflake

For the real platform, I would land daily files in S3 and ingest them into Snowflake raw tables using `COPY INTO` or Snowpipe. The dbt layer would then run unchanged except for the profile / adapter.

Example sketch:

```sql
create or replace stage raw.seloger_stage;
create or replace file format raw.csv_format
  type = csv
  skip_header = 1
  field_optionally_enclosed_by = '"';

copy into raw.listings
from @raw.seloger_stage/listings/
file_format = raw.csv_format
on_error = 'continue';

copy into raw.contacts
from @raw.seloger_stage/contacts/
file_format = raw.csv_format
on_error = 'continue';
```

That keeps the case aligned with their target stack without making the demo depend on cloud setup.

## Real-world considerations

### Schema drift
Land raw data with permissive ingestion, then promote new fields intentionally in staging. For example, a new `furnished_flag` can appear in raw first and later be documented and tested in dbt.

### Slowly changing attributes
For current-state reporting, overwrite is fine. For historical “as-was” analysis, snapshot listing attributes such as price and region. A sample snapshot is included.

### Late-arriving leads
Recompute a recent rolling window, or use incremental logic with backfill for the last 7-14 days so delayed leads update historical dates.

### Data contracts
Minimum upstream guarantees:
- primary keys present and unique per file
- valid timestamps with a defined timezone
- mandatory columns present
- controlled enums for `property_type` and `contact_source`
- no negative prices
- delivery SLA / naming convention

### Performance vs cost
For this small KPI mart, a table is appropriate. At larger scale, I would move to an incremental table by `metric_date` with a recent backfill window. A view is simplest but can become expensive for repeated dashboard queries.

## Example business takeaway

In the mock data, **apartments in Île-de-France** show the strongest lead density over the latest 14-day window, while parking inventory is materially weaker. That is enough to illustrate how marketplace, sales, or marketing teams could prioritize inventory types and regions.
