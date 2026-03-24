# Leads per Active Listing – Business Readout

## Snapshot window
- **Metric**: leads per active listing (leads_count / active_listing_count).
- **Source models**: mart_leads_per_active_listing plus analysis in nalyses/business_query.sql.
- **Data window**: latest 14 days ending on 2025-11-07 (per mart spine).
- **Reference tables**: nalyses/business_metric_summary_last_14d.csv for aggregated view and nalyses/business_metric_preview.csv for the daily detail.

## What the last 14 days say
1. **Île-de-France apartments are the benchmark** – 0.6012 leads per active listing, ~70 bps above any other region / asset mix, pointing to persistent lead demand relative to supply.
2. **Provence-Alpes-Côte d'Azur houses show improving density (0.3571)** as a handful of high-intent days (Oct 30, Nov 1-2) delivered 1.0 lead-per-listing spikes despite flat inventory.
3. **Occitanie apartments are mid-pack (0.2143)** but volatile: a run of zero-lead days between Nov 2-4 drags the average even after intermittent surges (Oct 28 and Nov 1).
4. **Parking categories drag the blended KPI** – Nouvelle-Aquitaine parking has been at 0.0 for two weeks and Occitanie parking barely hits 0.0714 on average, meaning leads are going elsewhere.

## Trend & variance call-outs
- **Spike days**: Île-de-France apartments reached 1.5 leads/listing on 2025-11-03, confirming the channel can absorb incremental inventory when marketed.
- **Drought periods**: Occitanie apartments posted three consecutive zero days (Nov 2-4) before recovering, hinting at campaign / visibility issues rather than structural supply shortages.
- **Low-volume swings**: Parking assets flip between 0 and 1 due to tiny inventory; keep them as a watchlist rather than headline KPI to avoid noise.

## Suggested business actions
1. **Double down on Île-de-France apartment acquisition** – keep onboarding comparable units and test premium placement since conversion remains high even at 0.6+ baseline.
2. **Stabilize Occitanie apartment visibility** – audit marketing spend and listing freshness for the Nov 2-4 drought window; aim for a floor of 0.25 by ensuring at least one lead per 4 listings daily.
3. **Revisit parking monetization** – with near-zero engagement, consider bundling parking slots with residential listings or pausing spend until differentiated demand is proven.
4. **Maintain Provence-Alpes-Côte d'Azur house momentum** – replicate the creative / partner promotions that spiked Nov 1-2, but monitor supply so lead density does not rely on undersized inventory.

Provide this readout alongside the csv artifacts in stakeholder updates so BI, sales, and marketing can react weekly.

