import streamlit as st
import clickhouse_connect
import pandas as pd
import pydeck as pdk
import plotly.express as px
import os

st.set_page_config(page_title="Public Safety Analytics", layout="wide", page_icon="🚨")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    h1 {
        background: linear-gradient(90deg, #ff7a18, #af002d 31%, #319197 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    div[data-testid="metric-container"] > div {
        color: #58a6ff; font-weight: 800; font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USER = "clickhouse"
CLICKHOUSE_PASSWORD = "clickhouse"
DATABASE = "public_safety"

@st.cache_resource
def get_client():
    try:
        return clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, 
            username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD, database=DATABASE
        )
    except Exception as e:
        st.error(f"Failed to connect to ClickHouse: {e}")
        return None

client = get_client()

@st.cache_data(ttl=2)
def fetch_kpis():
    if not client: return pd.DataFrame()
    query = """
    SELECT 
        COUNT(*) as total_incidents,
        MAX(incident_date) as last_update
    FROM (
        SELECT incident_id, incident_date FROM fact_incidents
        UNION ALL
        SELECT incident_id, incident_date FROM emergency_calls_live
    )
    """
    return client.query_df(query)

@st.cache_data(ttl=2)
def fetch_top_crimes():
    if not client: return pd.DataFrame()
    query = """
    SELECT 
        CASE 
            WHEN UPPER(type_name) LIKE '%THEFT%' THEN 'THEFT'
            WHEN UPPER(type_name) LIKE '%ASSAULT%' THEN 'ASSAULT'
            WHEN UPPER(type_name) LIKE '%NOISE%' THEN 'NOISE COMPLAINT'
            WHEN UPPER(type_name) LIKE '%BURGLARY%' THEN 'BURGLARY'
            ELSE UPPER(type_name) 
        END as normalized_type,
        COUNT(*) as incident_count
    FROM (
        SELECT t.type_name
        FROM fact_incidents f
        JOIN dim_incident_type t ON f.type_id = t.type_id
        UNION ALL
        SELECT incident_type as type_name
        FROM emergency_calls_live
    )
    GROUP BY normalized_type
    ORDER BY incident_count DESC
    LIMIT 10
    """
    return client.query_df(query)

@st.cache_data(ttl=2)
def fetch_time_series():
    if not client: return pd.DataFrame()
    query = """
    SELECT 
        incident_date as date,
        COUNT(incident_id) as incident_count
    FROM (
        SELECT incident_id, incident_date FROM fact_incidents
        UNION ALL
        SELECT incident_id, incident_date FROM emergency_calls_live
    )
    GROUP BY incident_date
    ORDER BY incident_date ASC
    """
    return client.query_df(query)

@st.cache_data(ttl=5)
def fetch_city_summaries():
    if not client: return pd.DataFrame()
    query = """
    SELECT 
        l.city,
        CASE 
            WHEN UPPER(t.type_name) LIKE '%THEFT%' THEN 'THEFT'
            WHEN UPPER(t.type_name) LIKE '%ASSAULT%' THEN 'ASSAULT'
            WHEN UPPER(t.type_name) LIKE '%NOISE%' THEN 'NOISE COMPLAINT'
            WHEN UPPER(t.type_name) LIKE '%BURGLARY%' THEN 'BURGLARY'
            ELSE UPPER(t.type_name) 
        END as incident_type,
        COUNT(*) as cnt
    FROM fact_incidents f
    JOIN dim_location l ON f.location_id = l.location_id
    JOIN dim_incident_type t ON f.type_id = t.type_id
    GROUP BY l.city, incident_type
    """
    df = client.query_df(query)
    
    live_query = """
    SELECT 
        'New_York' as city,
        CASE 
            WHEN UPPER(incident_type) LIKE '%THEFT%' THEN 'THEFT'
            WHEN UPPER(incident_type) LIKE '%ASSAULT%' THEN 'ASSAULT'
            WHEN UPPER(incident_type) LIKE '%NOISE%' THEN 'NOISE COMPLAINT'
            WHEN UPPER(incident_type) LIKE '%BURGLARY%' THEN 'BURGLARY'
            ELSE UPPER(incident_type) 
        END as incident_type,
        COUNT(*) as cnt
    FROM emergency_calls_live
    GROUP BY city, incident_type
    """
    live_df = client.query_df(live_query)
    if not live_df.empty:
        df = pd.concat([df, live_df]).groupby(['city', 'incident_type'], as_index=False).sum()
        
    if df.empty:
        return pd.DataFrame()
        
    summaries = []
    city_coords = {
        'New_York': (40.7128, -74.0060),
        'Philadelphia': (39.9526, -75.1652),
        'Chicago': (41.8781, -87.6298),
        'Los_Angeles': (34.0522, -118.2437),
        'London': (51.5074, -0.1278)
    }
    
    for city, group in df.groupby('city'):
        total = group['cnt'].sum()
        top_row = group.loc[group['cnt'].idxmax()]
        lat, lon = city_coords.get(city, (0.0, 0.0))
        summaries.append({
            'city': city.replace('_', ' '),
            'latitude': lat,
            'longitude': lon,
            'total_incidents': total,
            'top_incident': top_row['incident_type'],
            'top_incident_count': top_row['cnt'],
            'label': f"<b>{city.replace('_', ' ')}</b><br>({top_row['incident_type']})"
        })
    return pd.DataFrame(summaries)


st.title("🚨 Public Safety Analytics Command Center")
st.markdown("Real-time monitoring and analysis of crime and emergency incidents.")

if client is None:
    st.warning("Dashboard offline. Waiting for ClickHouse database...")
    st.stop()

kpi_df = fetch_kpis()
if not kpi_df.empty:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Incidents (Live + Batch)", f"{kpi_df['total_incidents'][0]:,}")
    with col2:
        st.metric("Last Update", str(kpi_df['last_update'][0]))
    st.markdown("---")

colA, colB = st.columns([2, 1])

with colA:
    st.subheader("📍 City-wise Top Incident Types")
    city_df = fetch_city_summaries()
    if not city_df.empty:
        # Use SVG-based scatter_geo (100% robust, does not require WebGL or Mapbox)
        color_map = {
            'THEFT': '#636EFA',            # Blue
            'NOISE COMPLAINT': '#EF553B', # Red
            'BURGLARY': '#00CC96',        # Green
            'ASSAULT': '#AB63FA',         # Purple
            'TRAFFIC ACCIDENT': '#FFA15A',# Orange
            'FIRE': '#19D3F3',            # Cyan
            'MEDICAL EMERGENCY': '#FF6692', # Pink
            'DOMESTIC DISTURBANCE': '#B6E880', # Light Green
            'SUSPICIOUS ACTIVITY': '#FF97FF', # Lavender
            'VANDALISM': '#FECB52'         # Gold
        }
        fig_map = px.scatter_geo(
            city_df,
            lat='latitude',
            lon='longitude',
            text='label', # Display city name and top incident underneath
            size='total_incidents', # Dot size proportional to total volume
            color='top_incident', # Dot color matches the primary problem type
            color_discrete_map=color_map, # Map colors explicitly
            hover_name='city',
            hover_data={
                'top_incident': True,
                'total_incidents': ':,',
                'latitude': False,
                'longitude': False
            },
            size_max=40, # Increase size max to make circles large and clear
            title=None
        )
        fig_map.update_traces(
            textposition='top center',
            textfont=dict(size=12)
        )
        for trace in fig_map.data:
            trace.textfont.color = trace.marker.color
        fig_map.update_layout(
            geo=dict(
                showland=True,
                landcolor="rgb(20, 24, 33)",
                showocean=True,
                oceancolor="rgb(10, 13, 20)",
                showlakes=True,
                lakecolor="rgb(10, 13, 20)",
                showcountries=True,
                countrycolor="rgb(50, 60, 80)",
                projection_type="equirectangular"
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            template="plotly_dark",
            height=550 # Increase map height to make it bigger and clearer
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No city summary data available.")

with colB:
    st.subheader("🔥 Top Incident Types")
    top_df = fetch_top_crimes()
    if not top_df.empty:
        fig_bar = px.bar(top_df, x='incident_count', y='normalized_type', orientation='h',
                         color='incident_count', color_continuous_scale='Reds',
                         template='plotly_dark')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No incident types available.")

st.subheader("📈 Incident Trends Over Time")
ts_df = fetch_time_series()
if not ts_df.empty:
    fig_line = px.line(ts_df, x='date', y='incident_count', template='plotly_dark')
    fig_line.update_traces(line_color='#ff7a18', line_width=3)
    fig_line.update_layout(margin=dict(l=0, r=0, t=0, b=0), xaxis_title="Date", yaxis_title="Number of Incidents")
    st.plotly_chart(fig_line, use_container_width=True)
