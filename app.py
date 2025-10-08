import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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

# 🌊 Add water video background (full screen)
video_bg = """
<video autoplay muted loop id="bgvid" style="
position: fixed; right:0; bottom:0;
min-width:100%; min-height:100%;
z-index:-1; object-fit:cover;">
<source src="https://cdn.pixabay.com/vimeo/397868884/waves-33833.mp4?width=1280&hash=0c8dbcd40279279f514de7b548b6162f6b1a45cf" type="video/mp4">
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
data_sheet_id = "1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1"  # Microplastic data
coord_sheet_id = "10K6rwt6BDcBzbmV2JSAc2wJH5SdLLH-LGiYthV9OMKw"  # Coordinates
rainfall_sheet_id = "1nRF6Tf6ZorBdEtU-fvV0Cyjv1Ts1LlL8"  # Rainfall data

try:
    df_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{data_sheet_id}/export?format=csv")
    df_coords = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{coord_sheet_id}/export?format=csv")
    df_rain = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{rainfall_sheet_id}/export?format=csv")

    # Merge rainfall data if available
    if all(col in df_rain.columns for col in ["River", "Location", "Rainfall_mm"]):
        df_data = pd.merge(df_data, df_rain[["River", "Location", "Rainfall_mm"]], on=["River", "Location"], how="left")

    st.success("✅ Live data loaded successfully!")
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.stop()

# Merge with coordinates
df = pd.merge(df_data, df_coords, on=["River", "Location"], how="left")

# Convert columns
df["DateTime"] = pd.to_datetime(df.get("DateTime", datetime.now()), errors="coerce")
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

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

if "🌐 All Rivers" in selected_rivers or len(selected_rivers) == 0:
    filtered_df = df.copy()
else:
    filtered_df = df[df["River"].isin(selected_rivers)]

# ------------------------------
# 📈 Key Stats
# ------------------------------
if not filtered_df.empty:
    avg_micro = filtered_df["Microplastic_ppm"].mean()
    avg_rain = filtered_df["Rainfall_mm"].mean() if "Rainfall_mm" in filtered_df else None
    last_update = filtered_df["DateTime"].max()

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><h3>💧 Avg Microplastic</h3><h2>{avg_micro:.2f} ppm</h2></div>", unsafe_allow_html=True)
    if avg_rain is not None:
        c2.markdown(f"<div class='metric-card'><h3>🌦️ Avg Rainfall</h3><h2>{avg_rain:.2f} mm</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><h3>📅 Last Updated</h3><h2>{last_update.strftime('%H:%M, %b %d')}</h2></div>", unsafe_allow_html=True)

# ------------------------------
# 📋 Data Table
# ------------------------------
st.subheader("📊 Recent Readings")
st.dataframe(filtered_df.tail(10), use_container_width=True)

# ------------------------------
# 🗺️ Map Visualization (Always Show All Locations)
# ------------------------------
st.subheader("🗺️ Microplastic Hotspot Map")

map_df = df.dropna(subset=["Latitude", "Longitude"]).copy()

# Rainfall emoji logic
def rain_emoji(rain):
    if pd.isna(rain): return "❔ No Data"
    elif rain < 5: return "☀️ Low"
    elif rain < 20: return "🌦️ Moderate"
    elif rain < 50: return "🌧️ High"
    else: return "⛈️ Very High"

if "Rainfall_mm" in map_df.columns:
    map_df["Rainfall_Level"] = map_df["Rainfall_mm"].apply(rain_emoji)
else:
    map_df["Rainfall_Level"] = "No Data"

# Always show all points
fig_map = px.scatter_mapbox(
    map_df,
    lat="Latitude",
    lon="Longitude",
    color="Microplastic_ppm",
    size="Microplastic_ppm",
    hover_name="Location",
    hover_data={
        "River": True,
        "Microplastic_ppm": True,
        "Rainfall_mm": True,
        "Rainfall_Level": True
    },
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
# ------------------------------
# 📈 Microplastic Trend Over Time (Light Mode)
# ------------------------------
st.subheader("📈 Microplastic Trend Over Time")

# Ensure DateTime and Microplastic_ppm are valid
if "DateTime" in df.columns:
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
else:
    st.warning("⚠️ No DateTime column found. Using current timestamps as fallback.")
    df["DateTime"] = pd.Timestamp.now()

df["Microplastic_ppm"] = pd.to_numeric(df["Microplastic_ppm"], errors="coerce")
filtered_df = df.dropna(subset=["DateTime", "Microplastic_ppm"])

if not filtered_df.empty:
    fig_micro = px.line(
        filtered_df,
        x="DateTime",
        y="Microplastic_ppm",
        color="River",
        markers=True,
        title="Microplastic Levels Over Time",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_micro.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0.7)",
        plot_bgcolor="rgba(255,255,255,0.85)",
        font=dict(color="#002b36", size=14),
        title_font=dict(size=20, color="#0077b6"),
        legend_title_text="River",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_micro, use_container_width=True)
else:
    st.info("No microplastic data available for selected rivers.")


# ------------------------------
# 🌧️ Rainfall Insights & Prediction (Light Mode Only)
# ------------------------------
if "Rainfall_mm" in df.columns:
    st.subheader("🌧️ Rainfall Insights & Prediction")

    rainfall_trend = (
        filtered_df.groupby("DateTime")["Rainfall_mm"]
        .mean()
        .reset_index()
        .sort_values("DateTime")
    )

    if not rainfall_trend.empty:
        rainfall_trend["Predicted_Rainfall_mm"] = rainfall_trend["Rainfall_mm"].rolling(3, min_periods=1).mean() * 1.05

        fig_rain = px.line(
            rainfall_trend,
            x="DateTime",
            y=["Rainfall_mm", "Predicted_Rainfall_mm"],
            markers=True,
            title="Rainfall Trend & Prediction",
            color_discrete_sequence=["#0077b6", "#00b4d8"]
        )
        fig_rain.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.85)",
            font=dict(color="#002b36", size=14),
            title_font=dict(size=20, color="#0077b6"),
            template="plotly_white"   # 👈 forces light background
        )
        st.plotly_chart(fig_rain, use_container_width=True)
    else:
        st.info("No rainfall data available to display trends.")

    # Debug helper (optional)
    # st.write("🧾 Debug: Rainfall data preview", rainfall_trend.head(10))
