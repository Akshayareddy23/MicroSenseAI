import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------
# 🌊 Page Configuration
# ------------------------------
st.set_page_config(page_title="MicroSense AI", page_icon="🌊", layout="wide")

# ------------------------------
# 🌗 Sidebar: Theme Toggle
# ------------------------------
st.sidebar.title("⚙️ Settings")
theme_mode = st.sidebar.radio("Choose Theme", ["🌞 Light Mode", "🌙 Dark Mode"])

# ------------------------------
# 💅 Custom CSS + Background Video
# ------------------------------
video_bg = """
<video autoplay muted loop id="bgvid" style="
position: fixed; right:0; bottom:0;
min-width:100%; min-height:100%;
z-index:-1; object-fit:cover;">
<source src="https://cdn.pixabay.com/vimeo/397868884/waves-33833.mp4?width=1280&hash=0c8dbcd40279279f514de7b548b6162f6b1a45cf" type="video/mp4">
</video>
"""
st.markdown(video_bg, unsafe_allow_html=True)

if theme_mode == "🌞 Light Mode":
    bg_color = "rgba(240,249,255,0.6)"
    card_bg = "linear-gradient(135deg, rgba(202,240,248,0.8), rgba(144,224,239,0.8))"
    text_color = "#002b36"
    accent_color = "#0077b6"
else:
    bg_color = "rgba(11,19,43,0.7)"
    card_bg = "linear-gradient(135deg, rgba(28,37,65,0.85), rgba(58,80,107,0.85))"
    text_color = "#f0f9ff"
    accent_color = "#5bc0be"

st.markdown(f"""
<style>
body {{
  color:{text_color};
  font-family:'Segoe UI',sans-serif;
}}
.main > div:first-child h1 {{
  color:{accent_color};
  text-align:center;
  font-size:2.6rem;
  font-weight:800;
  text-shadow:0px 0px 10px rgba(0,0,0,0.4);
}}
.metric-card {{
  background:{card_bg};
  padding:1.2rem;
  border-radius:1rem;
  box-shadow:0 4px 15px rgba(0,0,0,0.25);
  text-align:center;
  transition:all .3s;
  backdrop-filter:blur(10px);
}}
.metric-card:hover {{
  transform:scale(1.03);
}}
footer {{visibility:hidden;}}
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
data_sheet_id = "1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1"
coord_sheet_id = "10K6rwt6BDcBzbmV2JSAc2wJH5SdLLH-LGiYthV9OMKw"

try:
    df_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{data_sheet_id}/export?format=csv")
    df_coords = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{coord_sheet_id}/export?format=csv")
    st.success("✅ Live data loaded successfully from Google Sheets!")
except Exception as e:
    st.error(f"❌ Could not load Google Sheet data.\nError: {e}")
    st.stop()

# Merge & clean
df = pd.merge(df_data, df_coords, on=["River", "Location"], how="left")
if "DateTime" in df.columns:
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
else:
    df["DateTime"] = datetime.now()
for c in ["Latitude","Longitude"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ------------------------------
# 🌍 River Selection (All + Multi-Select)
# ------------------------------
# 🌍 River Selection (All + Multi-Select)
st.subheader("🌊 Select Rivers")

# Get unique rivers
river_list = sorted(df["River"].dropna().unique().tolist())

# Add "All Rivers" option manually at top
river_options = ["🌐 All Rivers"] + river_list

# Use multiselect widget
selected_rivers = st.multiselect(
    "Select one or more rivers to view data (or choose 🌐 All Rivers to show everything):",
    options=river_options,
    default=["🌐 All Rivers"]
)

# Logic to filter based on selection
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

    c1,c2,c3 = st.columns(3)
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
# 📈 Microplastic Trend
# ------------------------------
st.subheader("📈 Microplastic Trend Over Time")
if not filtered_df.empty:
    fig = px.line(
        filtered_df,
        x="DateTime",
        y="Microplastic_ppm",
        color="River",
        markers=True,
        title="Microplastic Levels Over Time",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_color,size=14),
        title_font=dict(size=20,color=accent_color)
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# 🗺️ Map Visualization
# ------------------------------
st.subheader("🗺️ Microplastic Hotspot Map")
valid_df = filtered_df.dropna(subset=["Latitude","Longitude"])
if not valid_df.empty:
    fig_map = px.scatter_mapbox(
        valid_df,
        lat="Latitude", lon="Longitude",
        color="Microplastic_ppm",
        size="Microplastic_ppm",
        hover_name="Location",
        hover_data=["River","Microplastic_ppm"],
        color_continuous_scale="Viridis",
        zoom=4, height=500,
        title="Microplastic Concentration by Location"
    )
    fig_map.update_layout(mapbox_style="open-street-map", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ No valid coordinates found for selected rivers.")

# ------------------------------
# 🌧️ Rainfall Prediction
# ------------------------------
if "Rainfall_mm" in df.columns:
    st.subheader("🌦️ Rainfall Prediction (Based on Past Trends)")
    rainfall_avg = filtered_df.groupby("Location", dropna=True)["Rainfall_mm"].mean().reset_index()
    rainfall_avg["Predicted_Rainfall_mm"] = rainfall_avg["Rainfall_mm"] * 1.1
    if not rainfall_avg.empty:
        fig_rain = px.bar(
            rainfall_avg,
            x="Location",
            y=["Rainfall_mm","Predicted_Rainfall_mm"],
            barmode="group",
            title="Current vs Predicted Rainfall (mm)",
            color_discrete_sequence=["#48cae4","#023e8a"] if theme_mode=="🌞 Light Mode" else ["#5bc0be","#3a506b"]
        )
        fig_rain.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=text_color,size=14)
        )
        st.plotly_chart(fig_rain, use_container_width=True)
