import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="MicroSense AI", page_icon="🌊", layout="wide")

st.title("🌊 MicroSense AI: Real-Time Microplastic Detection")

# Load default data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "DateTime": ["2025-10-07 08:00", "2025-10-07 09:00", "2025-10-07 10:00"],
        "River": ["Ganga", "Ganga", "Ganga"],
        "Location": ["Varanasi", "Varanasi", "Varanasi"],
        "Rainfall_mm": [5, 6, 3],
        "Microplastic_ppm": [8, 9, 10],
    })

df = st.session_state.data

# Sidebar - Add new reading
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
    st.session_state.data = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    st.success("✅ New reading added!")

# Dropdown to filter by river
selected_river = st.selectbox("🌊 Select a River", options=st.session_state.data["River"].unique())
filtered_df = st.session_state.data[st.session_state.data["River"] == selected_river]

# Display filtered data
st.subheader(f"Recent Microplastic Readings for {selected_river}")
st.dataframe(filtered_df.tail(10))

# Plot trend
st.subheader("Microplastic Trend Over Time")
fig = px.line(filtered_df, x="DateTime", y="Microplastic_ppm", color="River",
              markers=True, title=f"Microplastic Levels in {selected_river} Over Time")
st.plotly_chart(fig, use_container_width=True)

# Alert based on latest data
latest_value = filtered_df["Microplastic_ppm"].iloc[-1]
if latest_value < 5:
    st.success("✅ Safe levels of microplastic detected.")
elif latest_value < 10:
    st.warning("⚠️ Moderate contamination.")
else:
    st.error("🚨 High contamination detected! Immediate action required.")
