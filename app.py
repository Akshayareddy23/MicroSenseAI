# ------------------------------------------------
# 🌊 MICRO SENSE AI — Real-Time Microplastic Dashboard
# ------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# ------------------------------------------------
# 📄 Page Config & Background
# ------------------------------------------------
st.set_page_config(page_title="MicroSense AI", page_icon="🌊", layout="wide")

video_bg = """
<video autoplay muted loop id="bgvid" style="
position: fixed;
right: 0;
bottom: 0;
min-width: 100%;
min-height: 100%;
z-index: -1;
object-fit: cover;
opacity: 0.7;">
<source src="https://cdn.pixabay.com/vimeo/397868884/waves-33833.mp4?width=1280" type="video/mp4">
</video>
"""
st.markdown(video_bg, unsafe_allow_html=True)

st.markdown("""
<style>
body {
  color: black;
  font-family: 'Segoe UI', sans-serif;
}
.main > div:first-child h1 {
  color: black;
  text-align: center;
  font-size: 2.6rem;
  font-weight: 900;
  text-shadow: 0px 0px 6px rgba(255,255,255,0.6);
}
.metric-card {
  background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(210,210,210,0.85));
  padding: 1.2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  text-align: center;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}
.metric-card:hover {
  transform: scale(1.03);
}
.alert-box {
  background: rgba(255,0,0,0.2);
  border: 2px solid red;
  color: red;
  font-weight: bold;
  padding: 1rem;
  border-radius: 0.8rem;
  text-align: center;
  margin-bottom: 1.5rem;
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# 🌊 Header
# ------------------------------------------------
st.title("🌊 MicroSense AI — Smart River Microplastic & Rainfall Dashboard")
st.caption("Empowering clean rivers with real-time data & AI-driven microplastic detection")

# ------------------------------------------------
# 📊 Load Data from Google Sheets
# ------------------------------------------------
data_sheet_id = "1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1"  # Microplastic + Rainfall data
coord_sheet_id = "10K6rwt6BDcBzbmV2JSAc2wJH5SdLLH-LGiYthV9OMKw"  # Coordinates

try:
    df_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{data_sheet_id}/export?format=csv")
    df_coords = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{coord_sheet_id}/export?format=csv")

    df_data.columns = df_data.columns.str.strip().str.replace(" ", "_")
    df_coords.columns = df_coords.columns.str.strip().str.replace(" ", "_")

    df = pd.merge(df_data, df_coords, on=["River", "Location"], how="left")

    st.success("✅ Live data loaded successfully!")
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.stop()

# ------------------------------------------------
# 🧭 Data Cleaning
# ------------------------------------------------
df["DateTime"] = pd.to_datetime(df.get("DateTime", datetime.now()), errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
if "Rainfall_mm" in df.columns:
    df["Rainfall_mm"] = pd.to_numeric(df["Rainfall_mm"], errors="coerce")

# ------------------------------------------------
# 🌊 Select Rivers
# ------------------------------------------------
st.subheader("🌊 Select Rivers")
river_list = sorted(df["River"].dropna().unique().tolist())
river_options = ["🌐 All Rivers"] + river_list

selected_rivers = st.multiselect(
    "Select one or more rivers (or choose 🌐 All Rivers to view all):",
    options=river_options,
    default=["🌐 All Rivers"]
)
filtered_df = df if "🌐 All Rivers" in selected_rivers else df[df["River"].isin(selected_rivers)]

# ------------------------------------------------
# 🚨 Threshold Alert
# ------------------------------------------------
st.subheader("🚨 Alert System — Microplastic Safety Threshold")
threshold = st.slider("Set microplastic safety threshold (ppm):", 10, 100, 50)
exceeded = filtered_df[filtered_df["Microplastic_ppm"] > threshold]

if not exceeded.empty:
    st.markdown(f"<div class='alert-box'>⚠️ ALERT: {len(exceeded)} readings exceeded {threshold} ppm limit!</div>", unsafe_allow_html=True)
    st.dataframe(exceeded[["River", "Location", "Microplastic_ppm", "DateTime"]])
else:
    st.success(f"✅ All microplastic readings are below the {threshold} ppm threshold.")

# ------------------------------------------------
# 📈 Key Stats
# ------------------------------------------------
if not filtered_df.empty:
    avg_micro = filtered_df["Microplastic_ppm"].mean()
    avg_rain = filtered_df["Rainfall_mm"].mean() if "Rainfall_mm" in filtered_df else None
    last_update = filtered_df["DateTime"].max()

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><h3>💧 Avg Microplastic</h3><h2>{avg_micro:.2f} ppm</h2></div>", unsafe_allow_html=True)
    if avg_rain is not None and not pd.isna(avg_rain):
        c2.markdown(f"<div class='metric-card'><h3>🌦️ Avg Rainfall</h3><h2>{avg_rain:.2f} mm</h2></div>", unsafe_allow_html=True)
    else:
        c2.markdown(f"<div class='metric-card'><h3>🌦️ Avg Rainfall</h3><h2>No Data</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><h3>📅 Last Updated</h3><h2>{last_update.strftime('%H:%M, %b %d')}</h2></div>", unsafe_allow_html=True)

# ------------------------------------------------
# 🗺️ Map Visualization
# ------------------------------------------------
st.subheader("🗺️ Microplastic Hotspot Map")

map_df = df.dropna(subset=["Latitude", "Longitude", "Microplastic_ppm"]).copy()

if not map_df.empty:
    fig_map = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        color="Microplastic_ppm",
        size="Microplastic_ppm",
        hover_name="Location",
        hover_data={"River": True, "Rainfall_mm": True},
        color_continuous_scale="RdYlGn_r",
        zoom=4,
        height=550,
        title="🌍 Microplastic Concentration Across Rivers"
    )
    fig_map.update_layout(
        mapbox_style="open-street-map",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=60, b=10),
        font=dict(color="black", size=14),
        title_font=dict(size=20, color="black")
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ No valid coordinates to plot on map.")

# ------------------------------------------------
# 📈 Microplastic Trend
# ------------------------------------------------
st.subheader("📈 Microplastic Trend Over Time")

available_locations = filtered_df["Location"].dropna().unique().tolist()
selected_location = st.selectbox("📍 Select a Location", options=["🌍 All Locations"] + available_locations)

trend_df = filtered_df if selected_location == "🌍 All Locations" else filtered_df[filtered_df["Location"] == selected_location]
trend_df = trend_df.dropna(subset=["DateTime", "Microplastic_ppm"])

if not trend_df.empty:
    fig_micro = px.line(
        trend_df,
        x="DateTime",
        y="Microplastic_ppm",
        color="River",
        markers=True,
        title=f"Microplastic Levels {'for ' + selected_location if selected_location != '🌍 All Locations' else '(All Locations)'}",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_micro.add_hline(y=threshold, line_dash="dash", line_color="red",
                        annotation_text=f"Threshold: {threshold} ppm",
                        annotation_position="bottom right")
    fig_micro.update_layout(template="plotly_white")
    st.plotly_chart(fig_micro, use_container_width=True)
else:
    st.info("No data available for this location.")

# ------------------------------------------------
# 🌧️ Rainfall Trend
# ------------------------------------------------
if "Rainfall_mm" in filtered_df.columns:
    st.subheader("🌧️ Rainfall Trend Over Time")

    rain_df = trend_df.dropna(subset=["Rainfall_mm", "DateTime"])
    if not rain_df.empty:
        fig_rain = px.line(
            rain_df,
            x="DateTime",
            y="Rainfall_mm",
            color="River",
            markers=True,
            title=f"Rainfall Trend {'for ' + selected_location if selected_location != '🌍 All Locations' else '(All Locations)'}",
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig_rain.update_layout(template="plotly_white")
        st.plotly_chart(fig_rain, use_container_width=True)
    else:
        st.info("No rainfall data available for the selected location.")
