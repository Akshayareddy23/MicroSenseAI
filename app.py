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
st.markdown("""
<video autoplay muted loop playsinline style="
position: fixed;
right: 0;
bottom: 0;
min-width: 100%;
min-height: 100%;
object-fit: cover;
z-index: -1;
opacity: 0.6;">
<source src="https://cdn.pixabay.com/vimeo/397868884/waves-33833.mp4?width=1280" type="video/mp4">
</video>

<style>
/* Hide Streamlit header/footer */
header, footer {visibility: hidden;}

/* Glass effect for main app area */
[data-testid="stAppViewContainer"] > .main {
    background: rgba(255, 255, 255, 0.75);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 4px 25px rgba(0,0,0,0.2);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.85);
    border-radius: 20px;
}

/* Metric cards aesthetic */
.metric-card {
  background: linear-gradient(135deg, rgba(202,240,248,0.85), rgba(144,224,239,0.85));
  padding: 1.2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.25);
  text-align: center;
  backdrop-filter: blur(10px);
  transition: all 0.3s;
}
.metric-card:hover { transform: scale(1.03); }

div[data-testid="stPlotlyChart"] {
    background-color: rgba(255, 255, 255, 0.85);
    border-radius: 20px;
    padding: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
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

    if all(col in df_rain.columns for col in ["River", "Location", "Rainfall_mm"]):
        df_data = pd.merge(df_data, df_rain[["River", "Location", "Rainfall_mm"]], on=["River", "Location"], how="left")

    st.success("✅ Live data loaded successfully!")
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.stop()

# Merge with coordinates
df = pd.merge(df_data, df_coords, on=["River", "Location"], how="left")

# Type conversions
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
    avg_micro = filtered_df["Microplastic_ppm"].mean(skipna=True)
    avg_rain = filtered_df["Rainfall_mm"].mean(skipna=True) if "Rainfall_mm" in filtered_df.columns else None
    last_update = filtered_df["DateTime"].max()

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><h3>💧 Avg Microplastic</h3><h2>{avg_micro:.2f} ppm</h2></div>", unsafe_allow_html=True)
    if avg_rain is not None and not pd.isna(avg_rain):
        c2.markdown(f"<div class='metric-card'><h3>🌦️ Avg Rainfall</h3><h2>{avg_rain:.2f} mm</h2></div>", unsafe_allow_html=True)
    else:
        c2.markdown(f"<div class='metric-card'><h3>🌦️ Avg Rainfall</h3><h2>No data</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><h3>📅 Last Updated</h3><h2>{last_update.strftime('%H:%M, %b %d')}</h2></div>", unsafe_allow_html=True)

# ------------------------------
# 🗺️ Map Visualization
# ------------------------------
st.subheader("🗺️ Microplastic Hotspot Map")

map_df = df.dropna(subset=["Latitude", "Longitude"]).copy()

def rain_emoji(rain):
    if pd.isna(rain): return "❔ No Data"
    elif rain < 5: return "☀️ Low"
    elif rain < 20: return "🌦️ Moderate"
    elif rain < 50: return "🌧️ High"
    else: return "⛈️ Very High"

map_df["Rainfall_Level"] = map_df["Rainfall_mm"].apply(rain_emoji) if "Rainfall_mm" in map_df.columns else "No Data"

fig_map = px.scatter_mapbox(
    map_df,
    lat="Latitude",
    lon="Longitude",
    color="Microplastic_ppm",
    size="Microplastic_ppm",
    hover_name="Location",
    hover_data={"River": True, "Microplastic_ppm": True, "Rainfall_mm": True, "Rainfall_Level": True},
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
# 📈 Microplastic Trend Over Time
# ------------------------------
st.subheader("📈 Microplastic Trend Over Time")

available_locations = filtered_df["Location"].dropna().unique().tolist()
selected_location = st.selectbox("📍 Select a Location", ["🌍 All Locations"] + available_locations)

if selected_location != "🌍 All Locations":
    trend_df = filtered_df[filtered_df["Location"] == selected_location]
else:
    trend_df = filtered_df.copy()

trend_df = trend_df.dropna(subset=["DateTime", "Microplastic_ppm"])
trend_df["Microplastic_ppm"] = pd.to_numeric(trend_df["Microplastic_ppm"], errors="coerce")

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
    fig_micro.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0.7)",
        plot_bgcolor="rgba(255,255,255,0.85)",
        font=dict(color="#002b36", size=14),
        title_font=dict(size=20, color="#0077b6"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_micro, use_container_width=True)
else:
    st.info("No microplastic data available for the selected location.")

# ------------------------------
# 🌧️ Rainfall Insights & Prediction
# ------------------------------
st.subheader("🌧️ Rainfall Insights & Prediction")

rain_col = next((c for c in df.columns if 'rain' in c.lower()), None)

if rain_col:
    df[rain_col] = pd.to_numeric(df[rain_col], errors="coerce")
    available_locs = df["Location"].dropna().unique().tolist()
    selected_loc_rain = st.selectbox("📍 Select Location for Rainfall Trend", ["🌍 All Locations"] + available_locs)

    rain_df = df.copy() if selected_loc_rain == "🌍 All Locations" else df[df["Location"] == selected_loc_rain]
    rain_df["DateTime"] = pd.to_datetime(rain_df["DateTime"], errors="coerce")
    rain_df = rain_df.dropna(subset=["DateTime", rain_col])

    if not rain_df.empty:
        rain_df = rain_df.sort_values("DateTime")
        rain_df["Predicted_Rainfall_mm"] = rain_df[rain_col].rolling(3, min_periods=1).mean() * 1.05

        avg_rain = rain_df[rain_col].mean(skipna=True)
        avg_rain_text = f"{avg_rain:.2f} mm" if not pd.isna(avg_rain) else "No data"

        st.markdown(f"<div class='metric-card'><h3>🌦️ Avg Rainfall ({selected_loc_rain})</h3><h2>{avg_rain_text}</h2></div>", unsafe_allow_html=True)

        fig_rain = px.line(
            rain_df,
            x="DateTime",
            y=[rain_col, "Predicted_Rainfall_mm"],
            markers=True,
            title=f"Rainfall Trend & Prediction {'for ' + selected_loc_rain if selected_loc_rain != '🌍 All Locations' else '(All Locations)'}",
            color_discrete_sequence=["#0077b6", "#00b4d8"]
        )
        fig_rain.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(255,255,255,0.7)",
            plot_bgcolor="rgba(255,255,255,0.85)",
            font=dict(color="#002b36", size=14),
            title_font=dict(size=20, color="#0077b6"),
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig_rain, use_container_width=True)
    else:
        st.info("No valid rainfall data found for trend or prediction.")
else:
    st.warning("⚠️ No rainfall column found in dataset.")
