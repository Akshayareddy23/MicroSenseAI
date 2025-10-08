import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Setup ---
st.set_page_config(
    page_title="🌊 MicroSense AI Dashboard",
    layout="wide"
)

# --- Background Video Styling ---
st.markdown("""
    <style>
    .stApp {
        background: url("https://media.tenor.com/u2lRIkC6EqAAAAAd/water-ripples.gif");
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }
    h1, h2, h3, h4, h5, h6, p {
        color: black !important;
        font-weight: 800 !important;
        text-shadow: 0px 0px 4px white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🌊 MicroSense AI — Real-Time River Health & Rainfall Insights")

# --- Load Data from Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1nRF6Tf6ZorBdEtU-fvV0Cyjv1Ts1LlL8/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    st.success("✅ Live river & rainfall data loaded successfully!")
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.stop()

# --- Clean Data ---
df.columns = [c.strip() for c in df.columns]
if "Latitude" not in df.columns or "Longitude" not in df.columns:
    st.error("❌ Latitude and Longitude columns are required for map display.")
    st.stop()

# --- Sidebar ---
st.sidebar.header("🔍 Filter Options")
rivers = ["All Rivers"] + sorted(df["River"].dropna().unique().tolist())
selected_river = st.sidebar.selectbox("Select a River", rivers)

# --- Filter by River ---
if selected_river != "All Rivers":
    filtered_df = df[df["River"] == selected_river]
else:
    filtered_df = df

# --- Map Visualization ---
st.subheader("🗺️ River Locations & Microplastic Levels")

if not filtered_df.empty and "Latitude" in filtered_df.columns and "Longitude" in filtered_df.columns:
    fig_map = px.scatter_mapbox(
        df,  # Show all river points even if one river is selected
        lat="Latitude",
        lon="Longitude",
        color="Microplastic_ppm",
        size="Microplastic_ppm",
        hover_name="River",
        hover_data=["Location", "Microplastic_ppm"],
        color_continuous_scale="RdYlGn_r",
        zoom=5,
        height=500,
        title="🌍 River Network: Microplastic Concentration Overview"
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ No valid coordinate data available to plot the map.")

# --- Microplastic Trend Graph ---
st.subheader("📈 Microplastic Trend Over Time")

if "DateTime" in df.columns:
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")
    if selected_river != "All Rivers":
        fig_trend = px.line(
            filtered_df,
            x="DateTime",
            y="Microplastic_ppm",
            color="Location",
            markers=True,
            title=f"📊 Microplastic Trend in {selected_river}"
        )
    else:
        fig_trend = px.line(
            df,
            x="DateTime",
            y="Microplastic_ppm",
            color="River",
            markers=True,
            title="📊 Microplastic Trend Across All Rivers"
        )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.warning("⚠️ 'DateTime' column missing, unable to plot time trends.")

# --- Rainfall Graph ---
st.subheader("🌧️ Rainfall Trends by River")

if "Rainfall_mm" in df.columns:
    df["Rainfall_mm"] = pd.to_numeric(df["Rainfall_mm"], errors="coerce")
    avg_rain = df["Rainfall_mm"].mean(skipna=True)
    st.metric("🌦️ Average Rainfall", f"{avg_rain:.2f} mm")

    fig_rain = px.bar(
        df,
        x="River",
        y="Rainfall_mm",
        color="Rainfall_mm",
        color_continuous_scale="Blues",
        title="🌧️ Average Rainfall per River"
    )
    st.plotly_chart(fig_rain, use_container_width=True)
else:
    st.warning("⚠️ Rainfall data not found in this dataset.")

# --- Correlation Chart ---
st.subheader("🔬 Correlation: Rainfall vs Microplastic Concentration")

if "Rainfall_mm" in df.columns:
    corr_df = df.dropna(subset=["Microplastic_ppm", "Rainfall_mm"])
    fig_corr = px.scatter(
        corr_df,
        x="Rainfall_mm",
        y="Microplastic_ppm",
        color="River",
        title="💧 Impact of Rainfall on Microplastic Concentration",
        trendline="ols",
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_corr, use_container_width=True)
else:
    st.warning("⚠️ No rainfall data available to show correlation chart.")

# --- Footer ---
st.markdown("""
---
🎯 **MicroSense AI** — Empowering a cleaner, smarter water ecosystem through real-time environmental insights.  
💧 Developed with ❤️ using Streamlit, Plotly & Google Cloud.
""")
