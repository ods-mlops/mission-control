import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from mission_control import get_solar_flares, get_solar_image, analyze_with_image
from datetime import date


st.title("🛰️ Mission Control Anomaly Monitor 🚀")
st.markdown("Real-time solar flare analysis powered by NASA and Claude AI")

# Date picker and button
selected_date = st.date_input("Select observation date", value=date(2024, 1, 29))
run_button = st.button("Run Analysis")

if run_button:
    date_str = selected_date.strftime("%Y-%m-%d")
    
    with st.spinner("Fetching solar flare data..."):
        flares = get_solar_flares()
    
    
    with st.spinner("Retrieving solar image..."):
        solar_jpg = get_solar_image(date_str)

    
    with st.spinner("Running multimodal analysis..."):
        analysis = analyze_with_image(flares, solar_jpg)
    

    # Create two columns for side by side layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("Solar Image")
        st.image(solar_jpg)
        # hint: st.image() can accept raw jpg_bytes directly
    
    
    with col2:
        st.header("Anomaly Report")
        st.markdown(analysis)
    