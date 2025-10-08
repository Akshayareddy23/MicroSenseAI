import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(page_title="MicroSense AI", layout="wide")

# -------------------------------
# Background Water Video
# -------------------------------
st.markdown("""
    <style>
    body {
        background-color: #f2f6f9;
        color: black;
    }
    .stApp {
        background: url("https://cdn.coverr.co/videos/coverr-aerial-view-of-ocean-waves-1093/1080p.mp4");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    h1, h2, h3, h4 {
        color: black !important;
        font-weight: 800;
    }
    p, span, div {
        color: black !important;
    }
    .block-container {
        background-color: rgba(255, 255, 255, 0.75);
        padding: 2rem;
        border-radius: 15px;
        backdrop-filter: blur(8px);
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.title("🌊 Navigation")
page = st.sidebar.selectbox(
    "Choose a section:",
    ["🏠 Overview", "📈 Microplastic Trends", "🌧️ Rainfall Analysis", "🗺️ River Map"]
)

# -------------------------------
# Load Data (Local or Drive)
# -------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("microplastics_data.csv")  # <-- Your dataset path here
    return df

try:
    data = load_data()
    st.success("✅ Live data loaded successfully!")
except Exception as e:
    st.error(f"❌ Could not load data: {e}")
    st.stop()

# -------------------------------
# Overview Page
# -------------------------------
if page == "🏠 Overview":
    st.title("🌊 MicroSense AI: Intelligent River Health Monitoring")
    st.write("""
        Empowering clean rivers through real-time microplastic detection, rainfall insights,
        and predictive analytics. Building a data-driven environmental future. 🌍
    """)

    st.markdown("---")
    st.subheader("📊 Quick Stats")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rivers Monitored", data["River"].nunique())
    with col2:
        st.metric("Avg. Microplastic Concentration", f"{data['Microplastic(ppm)'].mean():.2f} ppm")
    with col3:
        st.metric("Avg. Rainfall", f"{data['Rainfall(mm)'].mean():.2f} mm")

# -------------------------------
# Microplastic Trends
# -------------------------------
elif page == "📈 Microplastic Trends":
    st.header("📈 Microplastic Trend Over Time")
    river_choice = st.selectbox("Select a river:", sorted(data["River"].unique()) + ["All"])

    if river_choice != "All":
        df_filtered = data[data["River"] == river_choice]
    else:
        df_filtered = data

    if not df_filtered.empty:
        fig = px.line(
            df_filtered,
            x="Date",
            y="Microplastic(ppm)",
            color="River" if river_choice == "All" else None,
            markers=True,
            title="📈 Microplastic Concentration Trends",
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for this selection.")

# -------------------------------
# Rainfall Analysis
# -------------------------------
elif page == "🌧️ Rainfall Analysis":
    st.header("🌧️ Rainfall vs Microplastic Correlation")
    st.write("Analyzing how rainfall affects microplastic concentration levels across different rivers.")

    corr_df = data.copy()
    fig_corr = px.scatter(
        corr_df,
        x="Rainfall(mm)",
        y="Microplastic(ppm)",
        color="River",
        trendline="ols",
        title="Rainfall Impact on Microplastic Concentration",
        template="plotly_white",
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    st.subheader("📅 Rainfall Trends Over Time")
    fig_rain = px.line(
        data,
        x="Date",
        y="Rainfall(mm)",
        color="River",
        markers=True,
        title="🌧️ Rainfall Patterns Over Time",
        template="plotly_white",
    )
    st.plotly_chart(fig_rain, use_container_width=True)

# -------------------------------
# River Map Visualization
# -------------------------------
elif page == "🗺️ River Map":
    st.header("🗺️ Microplastic Concentration Map")

    # Ensure lat/lon are valid
    map_df = data.dropna(subset=["Latitude", "Longitude"])
    if map_df.empty:
        st.warning("No valid coordinates found in dataset.")
    else:
        fig_map = px.scatter_mapbox(
            map_df,
            lat="Latitude",
            lon="Longitude",
            size="Microplastic(ppm)",
            color="Rainfall(mm)",
            hover_name="River",
            color_continuous_scale="Viridis",
            zoom=4,
            mapbox_style="open-street-map",
            title="🌍 Microplastic Concentration & Rainfall Impact",
        )
        st.plotly_chart(fig_map, use_container_width=True)
