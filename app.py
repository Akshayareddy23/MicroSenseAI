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
# 💅 Custom CSS Styling
# ------------------------------
if theme_mode == "🌞 Light Mode":
    bg_color = "#f0f9ff"
    card_bg = "linear-gradient(135deg, #caf0f8, #90e0ef)"
    text_color = "#003049"
    accent_color = "#0077b6"
else:
    bg_color = "#0b132b"
    card_bg = "linear-gradient(135deg, #1c2541, #3a506b)"
    text_color = "#f0f9ff"
    accent_color = "#5bc0be"

st.markdown(f"""
    <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Segoe UI', sans-serif;
        }}

        .main > div:first-child h1 {{
            color: {accent_color};
            text-align: center;
            font-size: 2.5rem;
            font-weight: 800;
        }}

        h2, h3 {{
            color: {accent_color};
        }}

        .metric-card {{
            background: {card_bg};
            padding: 1rem;
            border-radius: 1rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.25);
            text-align: center;
            transition: 0.3s;
        }}
        .metric-card:hover {{
            transform: scale(1.02);
        }}

        .stDataFrame {{
            border: 1px solid #90e0ef !important;
            border-radius: 10px;
        }}

        footer {{
            visibility: hidden;
        }}
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

data_csv_url = f"https://docs.google.com/spreadsheets/d/{data_sheet_id}/export?format=csv"
coord_csv_url = f"https://docs.google.com/spreadsheets/d/{coord_sheet_id}/export?format=csv"

try:
    df_data = pd.read_csv(data_csv_url)
    df_coords = pd.read_csv(coord_csv_url)
    st.success("✅ Live data loaded successfully from Google Sheets!")
except Exception as e:
    st.error(f"❌ Could not load Google Sheet data. Error: {e}")
    st.stop()

# Merge with coordinates
df = pd.merge(df_data, df_coords, on=["River", "Location"], how="left")

# Ensure DateTime
if "DateTime" in df.columns:
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors='coerce')
else:
    df["DateTime"] = datetime.now()

# ------------------------------
# 🌍 Filter Selection
# ------------------------------
selected_river = st.selectbox("🌊 Select a River", options=df["River"].unique())
filtered_df = df[df["River"] == selected_river]

# ------------------------------
# 📈 Key Stats Cards
# ------------------------------
if not filtered_df.empty:
    latest_row = filtered_df.iloc[-1]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💧 Microplastic</h3>
            <h2>{latest_row['Microplastic_ppm']} ppm</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if "Rainfall_mm" in latest_row:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌦️ Rainfall</h3>
                <h2>{latest_row['Rainfall_mm']} mm</h2>
            </div>
            """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅 Last Updated</h3>
            <h2>{latest_row['DateTime'].strftime("%H:%M, %b %d")}</h2>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------
# 📋 Data Table
# ------------------------------
st.subheader(f"📊 Recent Readings for {selected_river}")
st.dataframe(filtered_df.tail(10), use_container_width=True)

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
        title=f"Microplastic Levels in {selected_river} Over Time",
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, size=14)
    )
    st.plotly_chart(fig, use_container_width=True)

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
        color_continuous_scale="tealrose",
        zoom=4,
        height=500,
        title="Microplastic Concentration by Location"
    )
    fig_map.update_layout(
        mapbox_style="open-street-map",
        paper_bgcolor=bg_color
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ Coordinates missing in your data.")

# ------------------------------
# 🌧️ Rainfall Prediction
# ------------------------------
if "Rainfall_mm" in df.columns:
    st.subheader("🌦️ Rainfall Prediction")
    rainfall_avg = df.groupby("Location")["Rainfall_mm"].mean().reset_index()
    rainfall_avg["Predicted_Rainfall_mm"] = rainfall_avg["Rainfall_mm"] * 1.1

    fig_rain = px.bar(
        rainfall_avg,
        x="Location",
        y=["Rainfall_mm", "Predicted_Rainfall_mm"],
        barmode="group",
        title="Current vs Predicted Rainfall (mm)",
        color_discrete_sequence=["#48cae4", "#023e8a"] if theme_mode == "🌞 Light Mode" else ["#5bc0be", "#3a506b"]
    )
    fig_rain.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color, size=14)
    )
    st.plotly_chart(fig_rain, use_container_width=True)
