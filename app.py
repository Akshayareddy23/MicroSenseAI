import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import tempfile
import gspread
from google.oauth2.service_account import Credentials
import os

# ------------------------------
# 🌊 PAGE CONFIGURATION
# ------------------------------
st.set_page_config(page_title="MicroSense AI", page_icon="🌊", layout="wide")

# ------------------------------
# 🌅 WATER VIDEO BACKGROUND
# ------------------------------
video_bg = """
<video autoplay muted loop id="bgvid" style="
position: fixed;
right: 0;
bottom: 0;
min-width: 100%;
min-height: 100%;
z-index: -1;
object-fit: cover;
opacity: 0.6;">
<source src="https://cdn.pixabay.com/vimeo/397868884/waves-33833.mp4?width=1280" type="video/mp4">
</video>
"""
st.markdown(video_bg, unsafe_allow_html=True)

# ------------------------------
# 🎨 CUSTOM STYLING
# ------------------------------
st.markdown("""
<style>
body {
  color: #000000;
  font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3, h4, h5 {
  color: #000000 !important;
  font-weight: 900 !important;
}
.metric-card {
  background: rgba(255,255,255,0.8);
  padding: 1.2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.25);
  text-align: center;
  backdrop-filter: blur(10px);
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# 🌊 HEADER
# ------------------------------
st.title("🌊 MicroSense AI: Smart River Health Dashboard")
st.caption("AI-powered river microplastic and rainfall analytics — seamless, insightful, and sustainable.")

# ------------------------------
# 📊 LOAD GOOGLE SHEETS DATA
# ------------------------------
data_sheet_id = "1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1"  # Main Data (microplastics + rainfall)
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

# ------------------------------
# 🧭 DATA CLEANING
# ------------------------------
for col in ["Latitude", "Longitude", "Microplastic_ppm"]:
    if col not in df.columns:
        st.error(f"Missing column: {col}")
        st.stop()

df["DateTime"] = pd.to_datetime(df.get("DateTime", datetime.now()), errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
if "Rainfall_mm" in df.columns:
    df["Rainfall_mm"] = pd.to_numeric(df["Rainfall_mm"], errors="coerce")

# ------------------------------
# 🌍 RIVER SELECTION
# ------------------------------
st.subheader("🌊 Select Rivers to Visualize")
river_list = sorted(df["River"].dropna().unique().tolist())
river_options = ["🌐 All Rivers"] + river_list

selected_rivers = st.multiselect(
    "Select one or more rivers (or choose 🌐 All Rivers):",
    options=river_options,
    default=["🌐 All Rivers"]
)

filtered_df = df if "🌐 All Rivers" in selected_rivers else df[df["River"].isin(selected_rivers)]

# ------------------------------
# 📈 KEY STATS
# ------------------------------
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

# ------------------------------
# 🗺️ MAP VISUALIZATION
# ------------------------------
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
        color_continuous_scale="Turbo",
        zoom=4,
        height=550,
        title="🌍 Microplastic Concentration & Rainfall Correlation"
    )
    fig_map.update_layout(mapbox_style="carto-positron", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ No valid coordinates available for map visualization.")

# ------------------------------
# 📈 MICROPLASTIC TREND
# ------------------------------
st.subheader("📈 Microplastic Trend Over Time")

available_locations = filtered_df["Location"].dropna().unique().tolist()
selected_location = st.selectbox("📍 Select a Location", ["🌍 All Locations"] + available_locations)

trend_df = filtered_df if selected_location == "🌍 All Locations" else filtered_df[filtered_df["Location"] == selected_location]
trend_df = trend_df.dropna(subset=["DateTime", "Microplastic_ppm"])

if not trend_df.empty:
    fig_micro = px.line(
        trend_df,
        x="DateTime",
        y="Microplastic_ppm",
        color="River",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Dark2,
        title=f"Microplastic Levels Over Time {'for ' + selected_location if selected_location != '🌍 All Locations' else '(All Locations)'}"
    )
    st.plotly_chart(fig_micro, use_container_width=True)
else:
    st.info("No microplastic data available for this location.")

# ------------------------------
# 🌧️ RAINFALL TREND
# ------------------------------
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
            color_discrete_sequence=px.colors.sequential.Blues,
            title=f"Rainfall Trend Over Time {'for ' + selected_location if selected_location != '🌍 All Locations' else '(All Locations)'}"
        )
        st.plotly_chart(fig_rain, use_container_width=True)
    else:
        st.info("No rainfall data available for this location.")

# ------------------------------
# 📸 LIVE IMAGE MONITORING
# ------------------------------
st.header("📸 Live AI Image Monitoring")
st.caption("Upload a river sample image — AI detects microplastics and logs results directly into your Google Sheet.")

uploaded_file = st.file_uploader("Upload a water image", type=["jpg", "jpeg", "png"])

def analyze_microplastics(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
    count = cv2.countNonZero(thresh) // 100
    ppm = round(min(100, count / 10), 2)
    return count, ppm

def push_to_existing_sheet(river, location, micro_ppm, lat, lon):
    try:
        scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file("microsense-service-key.json", scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1").sheet1
        sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), river, location, micro_ppm, lat, lon])
        st.success("✅ Data added successfully to Google Sheet!")
    except Exception as e:
        st.error(f"❌ Could not upload to sheet: {e}")

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        img_path = tmp.name

    with st.spinner("Analyzing microplastics... 🔬"):
        count, ppm = analyze_microplastics(img_path)

    st.success(f"Detected approximately {count} microplastic particles")
    st.metric("Estimated Concentration", f"{ppm} ppm")

    river_name = st.text_input("🌊 River Name", value="Simulated River")
    location_name = st.text_input("📍 Location", value="Virtual Station")
    latitude = st.number_input("🧭 Latitude", value=25.34)
    longitude = st.number_input("🧭 Longitude", value=82.97)

    if st.button("📤 Save Result to Google Sheet"):
        push_to_existing_sheet(river_name, location_name, ppm, latitude, longitude)
        os.remove(img_path)
