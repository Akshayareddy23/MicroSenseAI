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
# Replace with your actual Google Sheet ID
sheet_id = "1f_U67643pkM5JK_KgN0BU1gqL_EMz6v1"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

try:
    df = pd.read_csv(csv_url)
    st.success("✅ Data loaded successfully from Google Sheets!")
except Exception as e:
    st.warning("⚠️ Could not load data from Google Sheets. Using default sample data.")
    df = pd.DataFrame({
        "DateTime": ["2025-10-07 08:00", "2025-10-07 09:00", "2025-10-07 10:00"],
        "River": ["Ganga", "Ganga", "Ganga"],
        "Location": ["Varanasi", "Varanasi", "Varanasi"],
        "Rainfall_mm": [5, 6, 3],
        "Microplastic_ppm": [8, 9, 10],
    })

# Ensure DateTime is proper datetime type
df["DateTime"] = pd.to_datetime(df["Timestamp"], errors='coerce')

# Store in session_state so user can add readings
if "data" not in st.session_state:
    st.session_state.data = df.copy()

# ------------------------------
# 🧾 Sidebar - Add New Reading
# ------------------------------
st.sidebar.header("➕ Add New Reading")
with st.sidebar.form("new_data"):
    river = st.text_input("River Name", "Ganga")
    location = st.text_input("Location", "Varanasi")
    rainfall = st.number_input("Rainfall (mm)", min_value=0, step=1)
    microplastic = st.number_input("Microplastic (ppm)", min_value=0, step=1)
    submit = st.form_submit_button("Add Reading")

if submit:
    new_row = {
        "DateTime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "River": river,
        "Location": location,
        "Rainfall_mm": rainfall,
        "Microplastic_ppm": microplastic,
    }
    st.session_state.data = pd.concat(
        [st.session_state.data, pd.DataFrame([new_row])],
        ignore_index=True
    )
    st.success("✅ New reading added successfully!")

# ------------------------------
# 🔍 Filter and Display Data
# ------------------------------
selected_river = st.selectbox(
    "🌊 Select a River",
    options=st.session_state.data["River"].unique()
)

filtered_df = st.session_state.data[
    st.session_state.data["River"] == selected_river
]

st.subheader(f"Recent Microplastic Readings for {selected_river}")
st.dataframe(filtered_df.tail(10))

# ------------------------------
# 📈 Plot Microplastic Trends
# ------------------------------
st.subheader("Microplastic Trend Over Time")

if not filtered_df.empty:
    fig = px.line(
        filtered_df,
        x="DateTime",
        y="Microplastic_ppm",
        color="River",
        markers=True,
        title=f"Microplastic Levels in {selected_river} Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

    # ------------------------------
    # 🚨 Alerts Based on Latest Value
    # ------------------------------
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
