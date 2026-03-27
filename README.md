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

## Automation scripts

### Windows (PowerShell)

```powershell
# full dbt lifecycle (creates .venv, installs deps, copies profile, runs dbt)
./scripts/setup_and_run_dbt.ps1

# launch Streamlit dashboard (optionally pass a fresh mart CSV)
./scripts/run_streamlit.ps1 -CsvPath analyses/business_metric_preview.csv -Port 8501
```

### macOS / Linux (bash)

```bash
chmod +x scripts/setup_and_run_dbt.sh scripts/run_streamlit.sh

# full dbt lifecycle
./scripts/setup_and_run_dbt.sh

# launch Streamlit dashboard
./scripts/run_streamlit.sh analyses/business_metric_preview.csv
```

Both helpers reuse `.venv` by default; pass a different path as the first argument if you want to isolate environments.

## Visualize the dbt lineage

```bash
dbt docs generate
dbt docs serve --port 8080
```

Open `http://localhost:8080` to explore the DAG (staging ➜ intermediate ➜ mart). For a static view, load `target/index.html` in any browser after `dbt docs generate`.

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

## Snowflake ingestion runbook

### External stage + COPY INTO job
1. Define external stages that point directly at the dated S3 prefixes delivered by upstream systems, e.g. `create stage raw.seloger_stage url='s3://seloger-data-prod/' ...`.
2. Land daily folders such as `s3://seloger-data-prod/listings/2026-03-25/` and `.../contacts/2026-03-25/`. A Dagster job (or similar) iterates over those prefixes, runs `COPY INTO raw.listings FROM @raw.seloger_stage/listings/2026-03-25/`, and records copy history for observability.
3. Staging dbt models always select from the Snowflake stage / raw tables instead of S3 directly, so downstream SQL stays identical whether the data arrived through a manual load or a scheduled job.

This COPY-based flow keeps tight control over retries, logging, and alerting—the things we normally want for SLA-backed data contracts.

### Snowpipe option + validations
- Snowpipe is the simpler zero-maintenance ingestion choice: create a pipe with `COPY INTO raw.listings FROM @raw.seloger_stage/listings/ pattern='.*[0-9]{4}-[0-9]{2}-[0-9]{2}/.*' FILE_FORMAT = ...`.
- Observability is lighter than a Dagster-managed job, but we can still emit pipe load history to dashboards or push notifications.
- We can embed validations directly in the pipe definition: use `COPY_OPTIONS = (ON_ERROR='ABORT_STATEMENT', MATCH_BY_COLUMN_NAME='CASE_INSENSITIVE')`, enforce required columns through file formats, and run `VALIDATION_MODE = 'RETURN_ERRORS'` dry runs before enabling auto-ingest.
- Managing `STAGE`, `FILE FORMAT`, and `PIPE` objects via Terraform keeps schema/contract changes reviewed like any other infrastructure-as-code change.

## Upstream data contract & bucket validation

Before Snowflake sees a file, an AWS Lambda (triggered by the S3 PUT event) should enforce minimum guarantees:
- Expect a control file per delivery (e.g. `control.json`) that states file counts, row counts, data date, and schema version; reject or quarantine deliveries that do not match.
- Validate the CSV / parquet headers match the contract (column presence, order when relevant, basic datatype inference) and log the results in CloudWatch for auditing.
- Sanity-check record counts (non-empty, within tolerance vs. previous day) so we catch truncation before analytics re-computes metrics.
- Only after those checks pass do we call Snowflake (COPY job or Snowpipe REST endpoint) to ingest the batch.

These validations keep "minimal viable data contract" enforcement outside the warehouse and provide a paper trail when upstream producers drift.

## Materialization & performance guidance

- Historical staging or intermediate models that scan large date ranges (e.g. the active-listing spine) should be incremental tables once volumes grow—process the latest `metric_date` window while retaining prior partitions.
- BI-facing marts (like `mart_leads_per_active_listing`) should be materialized tables for fast dashboards; smaller dimensional tables can also be fully materialized because refresh cost is low.
- Use views for temporary exploration or when we are iterating on a heavy query; once performance stabilizes, flip to an incremental/table materialization to control cost.
- This mix keeps Snowflake credits predictable while letting us scale up the freshness of the highest-value models.

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
- Lambda-level schema + row-count validation before Snowflake COPY / Snowpipe is invoked
- Control/manifest files in each S3 folder so we can cross-check completeness

### Performance vs cost
For this small KPI mart, a table is appropriate. At larger scale, I would move to an incremental table by `metric_date` with a recent backfill window. A view is simplest but can become expensive for repeated dashboard queries, so graduating heavy queries to incremental or table materializations keeps compute predictable.

## Example business takeaway

In the mock data, **apartments in Île-de-France** show the strongest lead density over the latest 14-day window, while parking inventory is materially weaker. That is enough to illustrate how marketplace, sales, or marketing teams could prioritize inventory types and regions.
