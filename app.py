import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------
# 🌊 PAGE CONFIGURATION
# ------------------------------
st.set_page_config(page_title="MicroSense AI Dashboard", page_icon="🌊", layout="wide")

# ------------------------------
# 💧 FULL WATER VIDEO BACKGROUND
# ------------------------------
st.markdown("""
<video autoplay muted loop id="bgvid" style="
position: fixed; right:0; bottom:0;
min-width:100%; min-height:100%;
z-index:-1; object-fit:cover; opacity:0.6;">
<source src="https://cdn.pixabay.com/vimeo/397868884/waves-33833.mp4?width=1280" type="video/mp4">
</video>
""", unsafe_allow_html=True)

# ------------------------------
# 🎨 STYLING (Light Mode + Overlay for Readability)
# ------------------------------
st.markdown("""
<style>
/* 🌊 GLOBAL BACKGROUND */
body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  background: transparent !important;
  color: #000000;  /* black text */
  font-family: 'Poppins', sans-serif;
}

/* 🏁 MAIN TITLE */
.main > div:first-child h1 {
  color: #000000; /* black */
  text-align: center;
  font-size: 3rem;
  font-weight: 900;
  letter-spacing: 1px;
  text-transform: uppercase;
  text-shadow: 2px 2px 6px rgba(255,255,255,0.5);
}

/* 💬 SUBTITLE / CAPTION */
.main > div:first-child p {
  color: #1a1a1a;  /* dark gray for readability */
  text-align: center;
  font-size: 1.1rem;
  font-weight: 500;
  text-shadow: 1px 1px 3px rgba(255,255,255,0.6);
}

/* 🧭 SECTION HEADINGS */
h2, h3, h4 {
  color: #000000; /* pure black */
  font-weight: 900;
  text-shadow: 1px 1px 4px rgba(255,255,255,0.6);
  border-left: 6px solid #000000;
  padding-left: 10px;
}

/* 📊 METRIC CARDS */
.metric-card {
  background: rgba(255, 255, 255, 0.85);
  padding: 1.4rem;
  border-radius: 1.2rem;
  box-shadow: 0 0 25px rgba(0, 0, 0, 0.3);
  text-align: center;
  color: #000000;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease-in-out;
}
.metric-card:hover {
  transform: scale(1.03);
  box-shadow: 0 0 35px rgba(0, 0, 0, 0.4);
}

/* ✅ ALERT BOXES */
.stAlert {
  background-color: rgba(255, 255, 255, 0.9) !important;
  border: 2px solid rgba(0, 0, 0, 0.6);
  color: #000000 !important;
  font-weight: 600;
}

/* 🧭 SIDEBAR */
[data-testid="stSidebar"] {
  background: rgba(255, 255, 255, 0.85) !important;
  color: #000000 !important;
}

/* 🚫 FOOTER */
footer {visibility: hidden;}
section.main > div {padding-top: 0rem;}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# 🧠 LOAD DATA (with caching for speed)
# ------------------------------
@st.cache_data(ttl=600)
def load_data():
    data_sheet_id = "1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1"  # Microplastic + rainfall data
    coord_sheet_id = "10K6rwt6BDcBzbmV2JSAc2wJH5SdLLH-LGiYthV9OMKw"  # Coordinates

    df_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{data_sheet_id}/export?format=csv")
    df_coords = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{coord_sheet_id}/export?format=csv")
    df = pd.merge(df_data, df_coords, on=["River", "Location"], how="left")

    df["DateTime"] = pd.to_datetime(df.get("DateTime", datetime.now()), errors="coerce")
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["Microplastic_ppm"] = pd.to_numeric(df["Microplastic_ppm"], errors="coerce")
    df["Rainfall_mm"] = pd.to_numeric(df.get("Rainfall_mm", 0), errors="coerce")
    return df

try:
    df = load_data()
    st.success("✅ Live data loaded successfully!")
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.stop()

# ------------------------------
# 🌍 RIVER & LOCATION FILTERS
# ------------------------------
st.sidebar.subheader("🌊 Filter Data")
river_list = sorted(df["River"].dropna().unique().tolist())
selected_rivers = st.sidebar.multiselect("Select Rivers:", ["🌐 All Rivers"] + river_list, default=["🌐 All Rivers"])

if "🌐 All Rivers" in selected_rivers or len(selected_rivers) == 0:
    filtered_df = df.copy()
else:
    filtered_df = df[df["River"].isin(selected_rivers)]

# Reset Filters
if st.sidebar.button("🔄 Reset Filters"):
    st.experimental_rerun()

# ------------------------------
# 🏠 OVERVIEW PAGE
# ------------------------------
if page == "🏠 Overview":
    st.header("💧 Environmental Health Overview")

    avg_micro = filtered_df["Microplastic_ppm"].mean()
    avg_rain = filtered_df["Rainfall_mm"].mean()
    last_update = filtered_df["DateTime"].max()

    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='metric-card'><h3>💧 Avg Microplastic</h3><h2>{avg_micro:.2f} ppm</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-card'><h3>🌦️ Avg Rainfall</h3><h2>{avg_rain:.2f} mm</h2></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-card'><h3>🕒 Last Update</h3><h2>{last_update.strftime('%H:%M, %b %d')}</h2></div>", unsafe_allow_html=True)

    st.subheader("📊 Top 5 Most Polluted Rivers")
    top_rivers = df.groupby("River")["Microplastic_ppm"].mean().nlargest(5).reset_index()
    st.bar_chart(top_rivers.set_index("River"))

# ------------------------------
# 🗺️ MAP PAGE
# ------------------------------
elif page == "🗺️ Map View":
    st.header("🗺️ Microplastic Hotspot Map")

    fig_map = px.scatter_mapbox(
        df.dropna(subset=["Latitude", "Longitude"]),
        lat="Latitude",
        lon="Longitude",
        color="Microplastic_ppm",
        size="Microplastic_ppm",
        hover_name="Location",
        hover_data={"River": True, "Rainfall_mm": True},
        color_continuous_scale="RdYlGn_r",
        zoom=4,
        height=550,
        title="Microplastic Concentration and Rainfall Influence"
    )
    fig_map.update_layout(mapbox_style="open-street-map", paper_bgcolor="rgba(0,0,0,0)", title_font=dict(size=20, color="#004b6b"))
    st.plotly_chart(fig_map, use_container_width=True)

# ------------------------------
# 📈 MICROPLASTIC TRENDS
# ------------------------------
elif page == "📈 Microplastic Trends":
    st.header("📈 Microplastic Levels Over Time")
    locs = filtered_df["Location"].dropna().unique().tolist()
    selected_loc = st.selectbox("Select Location:", ["🌍 All Locations"] + locs)

    if selected_loc != "🌍 All Locations":
        trend_df = filtered_df[filtered_df["Location"] == selected_loc]
    else:
        trend_df = filtered_df.copy()

    trend_df = trend_df.dropna(subset=["DateTime", "Microplastic_ppm"])
    fig_trend = px.line(
        trend_df,
        x="DateTime",
        y="Microplastic_ppm",
        color="River",
        markers=True,
        title=f"Microplastic Trends {'for ' + selected_loc if selected_loc != '🌍 All Locations' else '(All Locations)'}",
        color_discrete_sequence=px.colors.qualitative.Vivid
    )
    fig_trend.update_layout(template="plotly_white", plot_bgcolor="rgba(255,255,255,0.8)", title_font=dict(size=20, color="#004b6b"))
    st.plotly_chart(fig_trend, use_container_width=True)

# ------------------------------
# 🌧️ RAINFALL INSIGHTS
# ------------------------------
elif page == "🌧️ Rainfall Insights":
    st.header("🌧️ Rainfall Trends & Predictions")
    locs = filtered_df["Location"].dropna().unique().tolist()
    selected_loc_rain = st.selectbox("Select Location for Rainfall Trend:", ["🌍 All Locations"] + locs)

    rain_df = filtered_df if selected_loc_rain == "🌍 All Locations" else filtered_df[filtered_df["Location"] == selected_loc_rain]
    rain_df = rain_df.dropna(subset=["DateTime", "Rainfall_mm"]).sort_values("DateTime")
    if not rain_df.empty:
        rain_df["Predicted_Rainfall_mm"] = rain_df["Rainfall_mm"].rolling(3, min_periods=1).mean() * 1.05
        fig_rain = px.line(
            rain_df,
            x="DateTime",
            y=["Rainfall_mm", "Predicted_Rainfall_mm"],
            markers=True,
            title=f"Rainfall Trend & Forecast {'for ' + selected_loc_rain if selected_loc_rain != '🌍 All Locations' else '(All Locations)'}",
            color_discrete_sequence=["#0077b6", "#00b4d8"]
        )
        fig_rain.update_layout(template="plotly_white", plot_bgcolor="rgba(255,255,255,0.8)", title_font=dict(size=20, color="#004b6b"))
        st.plotly_chart(fig_rain, use_container_width=True)
    else:
        st.info("No rainfall data available for this location.")
# 📊 CORRELATION PAGE
elif page == "📊 Correlation Analysis":
    st.header("💧 Rainfall vs Microplastic Correlation")
    corr_df = filtered_df.dropna(subset=["Microplastic_ppm", "Rainfall_mm"])

    if not corr_df.empty:
        fig_corr = px.scatter(
            corr_df,
            x="Rainfall_mm",
            y="Microplastic_ppm",
            color="River",
            title="Rainfall vs Microplastic Concentration",
            color_continuous_scale="turbo",
            color_discrete_sequence=px.colors.sequential.Tealgrn_r,
            opacity=0.8
        )
        fig_corr.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0.7)",
            paper_bgcolor="rgba(0,0,0,0.7)",
            font=dict(color="#cbe6f3"),
            title_font=dict(size=20, color="#00e0ff"),
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Not enough data for correlation analysis.")
