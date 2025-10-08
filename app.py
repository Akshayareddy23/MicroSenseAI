import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ------------------------------
# 🌊 Page Configuration
# ------------------------------
st.set_page_config(page_title="MicroSense AI", page_icon="🌊", layout="wide")
st.title("🌊 MicroSense AI: Real-Time Microplastic Detection Dashboard")

# ------------------------------
# 📊 Load Data from Google Sheets
# ------------------------------
# Main data sheet (microplastic readings)
data_sheet_id = "1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1"
data_csv_url = f"https://docs.google.com/spreadsheets/d/{data_sheet_id}/export?format=csv"

# Coordinates sheet (river locations)
coord_sheet_id = "10K6rwt6BDcBzbmV2JSAc2wJH5SdLLH-LGiYthV9OMKw"
coord_csv_url = f"https://docs.google.com/spreadsheets/d/{coord_sheet_id}/export?format=csv"

try:
    df_data = pd.read_csv(data_csv_url)
    df_coords = pd.read_csv(coord_csv_url)
    st.success("✅ Live data loaded successfully from Google Sheets!")
except Exception as e:
    st.error(f"❌ Could not load Google Sheet data. Error: {e}")
    st.stop()

# Merge data with coordinates
df = pd.merge(df_data, df_coords, on=["River", "Location"], how="left")

# Ensure DateTime column
if "DateTime" in df.columns:
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors='coerce')
else:
    st.warning("⚠️ 'DateTime' column missing — timestamps will be generated.")
    df["DateTime"] = datetime.now()

# ------------------------------
# 🔍 Filter and Display Data
# ------------------------------
selected_river = st.selectbox(
    "🌊 Select a River",
    options=df["River"].unique()
)

filtered_df = df[df["River"] == selected_river]

st.subheader(f"📋 Latest Readings for {selected_river}")
st.dataframe(filtered_df.tail(10))

# ------------------------------
# 📈 Microplastic Trend Over Time
# ------------------------------
st.subheader("📈 Microplastic Trend Over Time")

if not filtered_df.empty:
    fig = px.line(
        filtered_df,
        x="DateTime",
        y="Microplastic_ppm",
        color="Location",
        markers=True,
        title=f"Microplastic Levels in {selected_river} Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Contamination Status
    latest_value = filtered_df["Microplastic_ppm"].iloc[-1]
    st.markdown("### 🔔 Contamination Status:")
    if latest_value < 5:
        st.success("✅ Safe levels of microplastic detected.")
    elif latest_value < 10:
        st.warning("⚠️ Moderate contamination detected.")
    else:
        st.error("🚨 High contamination detected! Immediate action required.")
else:
    st.info("No data available for the selected river.")

# ------------------------------
# 🗺️ Map Visualization
# ------------------------------
st.subheader("🗺️ Microplastic Hotspot Map")

if "Latitude" in df.columns and "Longitude" in df.columns:
    fig_map = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color="Microplastic_ppm",
        size="Microplastic_ppm",
        hover_name="Location",
        hover_data=["River", "Microplastic_ppm"],
        color_continuous_scale="RdYlGn_r",
        zoom=4,
        height=500,
        title="Microplastic Concentration by Location"
    )
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ Coordinates (Latitude, Longitude) missing in your data.")

# ------------------------------
# 🌧️ Simple Rainfall Prediction (Demo)
# ------------------------------
st.subheader("🌦️ Rainfall Prediction")

if "Rainfall_mm" in df.columns:
    rainfall_avg = df.groupby("Location")["Rainfall_mm"].mean().reset_index()
    rainfall_avg["Predicted_Rainfall_mm"] = rainfall_avg["Rainfall_mm"] * 1.1

    st.dataframe(rainfall_avg)

    fig_rain = px.bar(
        rainfall_avg,
        x="Location",
        y=["Rainfall_mm", "Predicted_Rainfall_mm"],
        barmode="group",
        title="Current vs Predicted Rainfall (mm)"
    )
    st.plotly_chart(fig_rain, use_container_width=True)
else:
    st.warning("⚠️ 'Rainfall_mm' column not found in your dataset.")
