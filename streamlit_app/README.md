# Streamlit dashboard addon

This folder is a standalone addon for the AVIV case submission. It is intentionally separate from the dbt project so you can drop it into the repo without changing the modeling structure.

## What it shows
The app visualizes the core mart KPI:
- `leads_per_active_listing`
- filtered by `metric_date`, `region`, and `property_type`

It expects a CSV with these columns:
- `metric_date`
- `region`
- `property_type`
- `active_listing_count`
- `leads_count`
- `leads_per_active_listing`

A demo CSV is bundled in `data/mart_leads_per_active_listing.csv`.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Interview positioning
Use this as a lightweight BI layer on top of the dbt mart. The narrative is:
1. dbt produces a trustworthy business-ready mart
2. Streamlit is just a simple presentation layer for the KPI
3. in production, this same mart could be exposed to Tableau, Looker, or another BI tool
