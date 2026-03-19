# 5-minute talk track

## 1) Problem framing
I treated this as a compact analytics pipeline for SeLoger-style listings and leads. The brief allows S3 **or local CSVs**, so I implemented a local CSV + DuckDB + dbt demo that still mirrors the production AWS -> Snowflake -> dbt architecture.

## 2) Core modeling choice
Because there is no explicit status column, I defined an active listing as one created on or before the metric date and updated in the last 30 days. That makes the KPI explainable while staying honest about source-system limits.

## 3) Quality controls
I added uniqueness, not-null, relationships, and accepted-values tests. These protect against duplicate leads, orphan contacts, and silent taxonomy drift.

## 4) Business value
The mart answers a real commercial question: where do we generate the most demand per available inventory? Teams can use it to spot strong regions, weak inventory classes, and candidates for pricing or marketing action.

## 5) Productionization
In production I would land files in S3, ingest to Snowflake with COPY INTO or Snowpipe, orchestrate dbt, monitor freshness and row counts, and reprocess a recent time window to absorb late-arriving leads.
