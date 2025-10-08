import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Connect to Google Sheets
def connect_to_sheets(sheet_name):
    # Define Google API scopes
    scopes = ["https://spreadsheets.google.com/feeds",
              "https://www.googleapis.com/auth/drive"]

    # Load credentials
    creds = Credentials.from_service_account_file(
        "microsense-service-key.json", scopes=scopes
    )

    # Authorize client
    client = gspread.authorize(creds)

    # Open Google Sheet by name (or use .open_by_key for sheet ID)
    sheet = client.open(sheet_name).sheet1
    return sheet
from datetime import datetime

def add_new_reading(sheet, river, location, microplastic_ppm, rainfall_mm):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, river, location, microplastic_ppm, rainfall_mm])


# ------------------------------
# 🌊 Page Configuration
# ------------------------------
st.set_page_config(page_title="MicroSense AI", page_icon="🌊", layout="wide")

# ------------------------------
# 💦 Full Water Background (Video)
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
opacity: 0.7;">
<source src="https://cdn.pixabay.com/vimeo/397868884/waves-33833.mp4?width=1280" type="video/mp4">
</video>
"""
st.markdown(video_bg, unsafe_allow_html=True)

# ------------------------------
# 🎨 Light Theme Styling
# ------------------------------
st.markdown("""
<style>
body {
  color: #002b36;
  font-family: 'Segoe UI', sans-serif;
}
.main > div:first-child h1 {
  color: #0077b6;
  text-align: center;
  font-size: 2.6rem;
  font-weight: 800;
  text-shadow: 0px 0px 10px rgba(0,0,0,0.3);
}
.metric-card {
  background: linear-gradient(135deg, rgba(202,240,248,0.85), rgba(144,224,239,0.85));
  padding: 1.2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.25);
  text-align: center;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}
.metric-card:hover {
  transform: scale(1.03);
}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# 🌊 Header
# ------------------------------
st.title("🌊 MicroSense AI: Real-Time Microplastic Detection Dashboard")
st.caption("Empowering clean rivers through live microplastic monitoring & rainfall insights")

# ------------------------------
# 📊 Load Data from Google Sheets
# ------------------------------
data_sheet_id = "1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1"  # Data + Rainfall
coord_sheet_id = "10K6rwt6BDcBzbmV2JSAc2wJH5SdLLH-LGiYthV9OMKw"  # Coordinates

try:
    df_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{data_sheet_id}/export?format=csv")
    df_coords = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{coord_sheet_id}/export?format=csv")

    df_data.columns = df_data.columns.str.strip().str.replace(" ", "_")
    df_coords.columns = df_coords.columns.str.strip().str.replace(" ", "_")

    st.success("✅ Live data loaded successfully!")
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.stop()

# Merge coordinates
df = pd.merge(df_data, df_coords, on=["River", "Location"], how="left")

# ------------------------------
# 🧭 Data Cleaning
# ------------------------------
for col in ["Latitude", "Longitude", "Microplastic_ppm"]:
    if col not in df.columns:
        st.error(f"Missing required column: {col}. Please check your Google Sheet.")
        st.stop()

df["DateTime"] = pd.to_datetime(df.get("DateTime", datetime.now()), errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
if "Rainfall_mm" in df.columns:
    df["Rainfall_mm"] = pd.to_numeric(df["Rainfall_mm"], errors="coerce")

# ------------------------------
# 🌍 River Selection
# ------------------------------
st.subheader("🌊 Select Rivers")
river_list = sorted(df["River"].dropna().unique().tolist())
river_options = ["🌐 All Rivers"] + river_list

selected_rivers = st.multiselect(
    "Select one or more rivers (or choose 🌐 All Rivers to view all):",
    options=river_options,
    default=["🌐 All Rivers"]
)

filtered_df = df if "🌐 All Rivers" in selected_rivers else df[df["River"].isin(selected_rivers)]

# ------------------------------
# 📈 Key Stats
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
# 📋 Data Table
# ------------------------------
st.subheader("📊 Recent Readings")
st.dataframe(filtered_df.tail(10), use_container_width=True)

# ------------------------------
# 🗺️ Map Visualization (Always Show All)
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
        color_continuous_scale="RdYlGn_r",
        zoom=4,
        height=550,
        title="🌍 Microplastic Concentration & Rainfall Impact"
    )
    fig_map.update_layout(
        mapbox_style="open-street-map",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=60, b=10),
        font=dict(color="#002b36", size=14),
        title_font=dict(size=20, color="#0077b6")
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ No valid location data available to plot map.")

# ------------------------------
# 📈 Microplastic Trend
# ------------------------------
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
        title=f"Microplastic Levels Over Time {'for ' + selected_location if selected_location != '🌍 All Locations' else '(All Locations)'}",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_micro.update_layout(template="plotly_white")
    st.plotly_chart(fig_micro, use_container_width=True)
else:
    st.info("No microplastic data available for the selected location.")

# ------------------------------
# 🌧️ Rainfall Trend
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
            title=f"Rainfall Trend Over Time {'for ' + selected_location if selected_location != '🌍 All Locations' else '(All Locations)'}",
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig_rain.update_layout(template="plotly_white")
        st.plotly_chart(fig_rain, use_container_width=True)
    else:
        st.info("No rainfall data available for the selected location.")# -------------------------------------------
# 📸 LIVE IMAGE MONITORING (Using existing Google Sheet)
# -------------------------------------------
import cv2
import numpy as np
import tempfile
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

st.header("📸 Live AI Image Monitoring")
st.caption("Upload a river water sample image to detect microplastics and log results into your existing Google Sheet 🌊")

uploaded_file = st.file_uploader("Upload a water image", type=["jpg", "jpeg", "png"])

# --- Simple AI-based Microplastic Detector ---
def analyze_microplastics(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blur = cv2.GaussianBlur(img, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV)
    count = cv2.countNonZero(thresh) // 100
    ppm = round(min(100, count / 10), 2)
    return count, ppm

# --- Upload result to existing Google Sheet ---
def push_to_existing_sheet(river, location, micro_ppm, lat, lon):
    try:
        # Google API authorization
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        client = gspread.authorize(creds)

        # Use your OLD sheet here ✅
        sheet = client.open_by_key("10K6rwt6BDcBzbmV2JSAc2wJH5SdLLH-LGiYthV9OMKw").sheet1

        # Append the new data row
        sheet.append_row([
            river,
            location,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            micro_ppm,
            "",
            lat,
            lon
        ])

        st.success("✅ Added to your existing Google Sheet successfully!")
    except Exception as e:
        st.error(f"❌ Could not upload: {e}")

# --- Handle upload + processing ---
if uploaded_file is not None:
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

    if st.button("📤 Save Result to Sheet"):
        push_to_existing_sheet(river_name, location_name, ppm, latitude, longitude)
        os.remove(img_path)


