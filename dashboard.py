import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import timedelta
import pydeck as pdk

st.set_page_config(page_title="🔋 EV Charging Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    .main { background-color: #f7f9fc; }
    h1, h2, h3, h4 { color: #2e3b4e; }
    .stMetric { font-size: 1.1rem !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔌 EV Charging Station Real-Time Dashboard")

# File paths
sensor_data_file = "ev_charging_data.csv"
forecast_file = "realtime_forecast.csv"

# File check
if not os.path.exists(sensor_data_file):
    st.warning("Sensor data file not found.")
    st.stop()
if not os.path.exists(forecast_file):
    st.warning("Forecast data file not found.")
    st.stop()

# Load Sensor Data
df = pd.read_csv(sensor_data_file)
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
df = df.set_index("timestamp").sort_index()

# Sidebar Filter
st.sidebar.header("🧰 Filter Options")
time_window = st.sidebar.slider("Display Last N Minutes", min_value=2, max_value=120, value=20, step=2)

# Define time range
end_time = df.index.max()
start_time = end_time - timedelta(minutes=time_window)
df_filtered = df[(df.index >= start_time) & (df.index <= end_time)]

# Load Forecast Data
forecast_df = pd.read_csv(forecast_file, index_col=0)
forecast_df.index = pd.to_datetime(forecast_df.index)

# KPI Metrics
latest = df_filtered.iloc[-1]
st.markdown("### ⚡ Key Metrics")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Active Sessions", f"{latest['active_sessions']}")
kpi2.metric("Voltage (V)", f"{latest['voltage']}")
kpi3.metric("Current (A)", f"{latest['current']}")
kpi4.metric("Temperature (°C)", f"{latest['temperature']}")

# Visualizations
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Active EV Sessions Over Time")
    fig = px.line(df_filtered, y="active_sessions", title="EV Sessions", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔋 Voltage & Current")
    fig2 = px.line(df_filtered, y=["voltage", "current"], title="Power Readings", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("🌡️ Temp & Proximity Readings")
    fig3 = px.line(df_filtered, y=["temperature", "proximity"], title="Environmental Sensors", template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📈 Forecast: EV Demand (ARIMA)")
    fig4 = px.line(forecast_df, title="Predicted Active Sessions", template="plotly_white")
    st.plotly_chart(fig4, use_container_width=True)

# ------------------- 🔥 Heatmap and Scatterplot Map -------------------
st.markdown("---")
st.subheader("🗺️ Real-Time EV Station Map (India)")

# Get latest location data
latest_data = df_filtered.tail(20).copy()  # show last 20 for heatmap

# Fallback for missing lat/lon
if "lat" not in latest_data.columns:
    latest_data["lat"] = 28.61
if "lon" not in latest_data.columns:
    latest_data["lon"] = 77.23
latest_data["lat"].fillna(28.61, inplace=True)
latest_data["lon"].fillna(77.23, inplace=True)

# Scatterplot Layer
scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=latest_data,
    get_position='[lon, lat]',
    get_color='[0, 200, 0, 160]',
    get_radius=500,
    pickable=True,
)

# Heatmap Layer
heat_layer = pdk.Layer(
    "HeatmapLayer",
    data=latest_data,
    get_position='[lon, lat]',
    aggregation="'MEAN'",
    get_weight='active_sessions',
    radiusPixels=60,
)

# View settings
view_state = pdk.ViewState(
    latitude=latest_data["lat"].mean(),
    longitude=latest_data["lon"].mean(),
    zoom=11,
    pitch=30,
)

# Combine layers
r = pdk.Deck(
    layers=[heat_layer, scatter_layer],
    initial_view_state=view_state,
    tooltip={"text": "🔋 Voltage: {voltage} V\n⚡ Current: {current} A\n🔥 Temp: {temperature} °C\n🚗 Sessions: {active_sessions}"},
)

st.pydeck_chart(r)

# ------------------ 📄 Data Tables ------------------
st.markdown("---")
st.subheader("🧾 Raw Data Snapshots")
with st.expander("📌 Latest Sensor Data"):
    st.dataframe(df_filtered.tail(10), use_container_width=True)
with st.expander("📌 Forecast Data"):
    st.dataframe(forecast_df.tail(5), use_container_width=True)

st.caption("⏱️ Auto-refresh by rerunning the app or using Streamlit's auto-refresh plugin.")
