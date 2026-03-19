from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title='AVIV Case Dashboard', layout='wide')

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
DEFAULT_CSV = DATA_DIR / 'mart_leads_per_active_listing.csv'

@st.cache_data
def load_data(uploaded_file=None) -> pd.DataFrame:
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif DEFAULT_CSV.exists():
        df = pd.read_csv(DEFAULT_CSV)
    else:
        raise FileNotFoundError('No mart CSV found.')

    df['metric_date'] = pd.to_datetime(df['metric_date'])
    numeric_cols = [
        'active_listing_count',
        'leads_count',
        'leads_per_active_listing'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

st.title('AVIV / SeLoger Analytics Case Dashboard')
st.caption('Local Streamlit addon for the dbt mart `mart_leads_per_active_listing`.')

with st.sidebar:
    st.header('Data source')
    uploaded = st.file_uploader('Upload mart CSV (optional)', type=['csv'])
    st.markdown('If you do not upload a file, the app uses the bundled demo CSV.')

try:
    df = load_data(uploaded)
except Exception as e:
    st.error(f'Could not load data: {e}')
    st.stop()

min_date = df['metric_date'].min().date()
max_date = df['metric_date'].max().date()

with st.sidebar:
    st.header('Filters')
    date_range = st.date_input('Metric date range', value=(min_date, max_date), min_value=min_date, max_value=max_date)
    regions = sorted(df['region'].dropna().unique().tolist())
    property_types = sorted(df['property_type'].dropna().unique().tolist())
    selected_regions = st.multiselect('Region', regions, default=regions)
    selected_property_types = st.multiselect('Property type', property_types, default=property_types)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    (df['metric_date'].dt.date >= start_date) &
    (df['metric_date'].dt.date <= end_date) &
    (df['region'].isin(selected_regions)) &
    (df['property_type'].isin(selected_property_types))
].copy()

if filtered.empty:
    st.warning('No rows match the current filters.')
    st.stop()

latest_date = filtered['metric_date'].max()
latest = filtered[filtered['metric_date'] == latest_date].copy()

k1, k2, k3 = st.columns(3)
k1.metric('Latest metric date', latest_date.strftime('%Y-%m-%d'))
k2.metric('Total leads', f"{int(latest['leads_count'].sum()):,}")
k3.metric('Avg leads / active listing', f"{latest['leads_per_active_listing'].mean():.2f}")

st.subheader('Trend over time')
trend = filtered.groupby('metric_date', as_index=False).agg(
    active_listing_count=('active_listing_count', 'sum'),
    leads_count=('leads_count', 'sum')
)
trend['leads_per_active_listing'] = trend['leads_count'] / trend['active_listing_count'].replace(0, pd.NA)

trend_chart = alt.Chart(trend).mark_line(point=True).encode(
    x=alt.X('metric_date:T', title='Metric date'),
    y=alt.Y('leads_per_active_listing:Q', title='Leads per active listing'),
    tooltip=['metric_date:T', 'active_listing_count:Q', 'leads_count:Q', 'leads_per_active_listing:Q']
).properties(height=320)

st.altair_chart(trend_chart, use_container_width=True)

left, right = st.columns([1, 1])

with left:
    st.subheader('Latest snapshot by region')
    region_rank = latest.groupby('region', as_index=False).agg(
        active_listing_count=('active_listing_count', 'sum'),
        leads_count=('leads_count', 'sum')
    )
    region_rank['leads_per_active_listing'] = region_rank['leads_count'] / region_rank['active_listing_count'].replace(0, pd.NA)
    region_rank = region_rank.sort_values('leads_per_active_listing', ascending=False)

    region_chart = alt.Chart(region_rank).mark_bar().encode(
        x=alt.X('leads_per_active_listing:Q', title='Leads per active listing'),
        y=alt.Y('region:N', sort='-x', title='Region'),
        tooltip=['region:N', 'active_listing_count:Q', 'leads_count:Q', 'leads_per_active_listing:Q']
    ).properties(height=320)
    st.altair_chart(region_chart, use_container_width=True)

with right:
    st.subheader('Latest snapshot by property type')
    type_rank = latest.groupby('property_type', as_index=False).agg(
        active_listing_count=('active_listing_count', 'sum'),
        leads_count=('leads_count', 'sum')
    )
    type_rank['leads_per_active_listing'] = type_rank['leads_count'] / type_rank['active_listing_count'].replace(0, pd.NA)
    type_rank = type_rank.sort_values('leads_per_active_listing', ascending=False)

    type_chart = alt.Chart(type_rank).mark_bar().encode(
        x=alt.X('leads_per_active_listing:Q', title='Leads per active listing'),
        y=alt.Y('property_type:N', sort='-x', title='Property type'),
        tooltip=['property_type:N', 'active_listing_count:Q', 'leads_count:Q', 'leads_per_active_listing:Q']
    ).properties(height=320)
    st.altair_chart(type_chart, use_container_width=True)

st.subheader('Latest KPI table')
show_cols = ['metric_date', 'region', 'property_type', 'active_listing_count', 'leads_count', 'leads_per_active_listing']
st.dataframe(latest[show_cols].sort_values(['leads_per_active_listing', 'leads_count'], ascending=[False, False]), use_container_width=True)

with st.expander('How to use this in the interview'):
    st.markdown(
        '- Say this dashboard sits on top of the dbt mart, not on raw CSVs directly.\n'
        '- Lead with the KPI trend, then compare the latest snapshot by region and property type.\n'
        '- Call out that the “active listing” rule is a pragmatic proxy because the source has no explicit status field.'
    )
