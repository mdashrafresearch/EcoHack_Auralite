import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import folium
from streamlit_folium import folium_static
import numpy as np

# Page config
st.set_page_config(
    page_title="Auralite v2.0 - Detection Dashboard",
    page_icon="🌍",
    layout="wide",
)

# API endpoint
API_URL = "http://localhost:8000"

st.title("🌍 Auralite: Enhanced Illegal Mining Detection")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🔧 Monitoring Controls")
    lat = st.number_input("Latitude", value=-3.0, format="%.4f")
    lon = st.number_input("Longitude", value=-65.0, format="%.4f")
    radius = st.slider("Radius (km)", 1, 50, 10)
    
    st.subheader("Time Range")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_picker = st.date_input("Start Date", start_date)
    end_picker = st.date_input("End Date", end_date)
    
    if st.button("🚨 Run Real-time Detection", type="primary"):
        # Call API
        try:
            payload = {
                "location": {"lat": lat, "lon": lon, "radius": float(radius)},
                "start_date": start_picker.isoformat(),
                "end_date": end_picker.isoformat()
            }
            resp = requests.post(f"{API_URL}/api/detect", json=payload)
            if resp.status_code == 200:
                st.session_state['last_detection'] = resp.json()
                st.success("Detection complete!")
            else:
                st.error(f"API Error: {resp.text}")
        except Exception as e:
            st.error(f"Connection failed: {e}")

# Metrics Row
c1, c2, c3 = st.columns(3)
with c1: st.metric("System Status", "ONLINE", delta="Healthy")
with c2: st.metric("Active Sensors", "24", delta="+2")
with c3: st.metric("Alert Intensity", "MEDIUM", delta="-5%", delta_color="inverse")

st.markdown("---")

# Map and Alarms
col_map, col_alerts = st.columns([2, 1])

with col_map:
    st.subheader("🗺️ Live Monitoring Map")
    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Circle(
        radius=radius * 1000,
        location=[lat, lon],
        popup="AOI",
        color="blue", fill=True, fillOpacity=0.1
    ).add_to(m)
    
    # Show last detection if available
    if 'last_detection' in st.session_state:
        det = st.session_state['last_detection']
        color = "red" if det['is_mining'] else "green"
        folium.Marker(
            [det['location']['lat'], det['location']['lon']],
            popup=f"Mining: {det['is_mining']}\nConfidence: {det['confidence']:.2f}",
            icon=folium.Icon(color=color, icon="bolt" if det['is_mining'] else "leaf")
        ).add_to(m)
        
    folium_static(m, width=700)

with col_alerts:
    st.subheader("🚨 Recent Alerts")
    # Dummy alerts
    alerts = [
        {"time": "10m ago", "loc": "Sector A", "sev": "HIGH", "type": "Excavator"},
        {"time": "1h ago", "loc": "Sector C", "sev": "MED", "type": "Vegetation Loss"},
        {"time": "4h ago", "loc": "Sector B", "sev": "HIGH", "type": "Drilling"},
    ]
    for a in alerts:
        if a['sev'] == "HIGH": st.error(f"**{a['time']}** - {a['loc']}: {a['type']}")
        else: st.warning(f"**{a['time']}** - {a['loc']}: {a['type']}")

# Analytics Tabs
st.subheader("📊 Multi-Modal Analysis")
tab1, tab2, tab3 = st.tabs(["Satellite (NDVI)", "Nightlight", "Acoustic"])

with tab1:
    # NDVI Chart
    dummy_dates = pd.date_range(end=datetime.now(), periods=10, freq='3D')
    dummy_ndvi = [0.6, 0.58, 0.55, 0.4, 0.35, 0.32, 0.34, 0.36, 0.35, 0.34]
    fig = px.line(x=dummy_dates, y=dummy_ndvi, title="Vegetation Health (NDVI) Trend")
    fig.add_hline(y=0.4, line_dash="dash", line_color="red")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Nightlight chart
    dummy_rad = np.random.uniform(5, 25, 10)
    fig = px.bar(x=dummy_dates, y=dummy_rad, title="Nightlight Radiance (VIIRS)")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # Acoustic Features
    st.info("Acoustic sensors processing YAMNet deep features...")
    st.bar_chart(np.random.randn(20, 3))

st.markdown("---")
st.caption("© 2024 Auralite System - Powered by DeepMind Antigravity")
