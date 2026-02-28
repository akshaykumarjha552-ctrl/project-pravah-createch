import streamlit as st
import numpy as np

st.set_page_config(page_title="Project Pravah", layout="wide", initial_sidebar_state="expanded")
st.title("PROJECT PRAVAH – Dynamic Line Rating Prototype")

st.markdown("""
<h1 style='text-align: center; color: #0E4D64;'>
PROJECT PRAVAH — Dynamic Line Rating Intelligence Engine
</h1>
""", unsafe_allow_html=True)
st.header("Weather Inputs")

col1, col2, col3 = st.columns(3)

with col1:
    wind_speed = st.slider("Wind Speed (m/s)", 0.1, 10.0, 1.0)

with col2:
    ambient_temp = st.slider("Ambient Temperature (°C)", 10.0, 50.0, 35.0)

with col3:
    solar_radiation = st.slider("Solar Radiation (W/m²)", 0, 1200, 800)




st.divider()
st.header("Live Grid Loading")

live_loading = st.slider("Current Line Loading (A)", 500, 1500, 1100)
st.divider()

st.header("Conductor Parameters (ACSR Zebra Approximation)")

R = 0.0001  # Ohm/m (approx resistance)
D = 0.0286  # Diameter in meters
emissivity = 0.5
absorptivity = 0.5
T_max = 90  # Design thermal limit °C

# Heat Balance Model
def calculate_dlr(wind_speed, ambient_temp, solar_radiation, static_rating):    
    T_surface = T_max
    
    # Solar Heat Gain
    Qs = absorptivity * solar_radiation * D
    
    # Convective Cooling (simplified)
    Qc = 3.5 * wind_speed * (T_surface - ambient_temp)
    
    # Radiative Cooling (simplified)
    Qr = emissivity * 5.67e-8 * ((T_surface + 273)**4 - (ambient_temp + 273)**4)
    
    # Allowable Ohmic Heating
    I_raw = np.sqrt(max((Qc + Qr - Qs) / R, 0))

    # Apply engineering safety cap (max 35% unlock)
    I = min(I_raw, static_rating * 1.35)
    
    return I

static_rating = 1000

dynamic_rating = calculate_dlr(wind_speed, ambient_temp, solar_radiation, static_rating)



unlock_percent = ((dynamic_rating - static_rating) / static_rating) * 100

st.markdown("## Grid Capacity Overview")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Static Rating (A)", f"{static_rating:.0f}")

with kpi2:
    st.metric("Dynamic Rating (A)", f"{dynamic_rating:.0f}", 
              delta=f"{dynamic_rating - static_rating:.0f} A")

with kpi3:
    st.metric("Capacity Unlock (%)", f"{unlock_percent:.1f}%")

with kpi4:
    st.metric("Live Loading (A)", f"{live_loading:.0f}")

st.divider()

st.subheader("Congestion Analysis")

if live_loading > static_rating and live_loading <= dynamic_rating:
    st.success("Static grid shows congestion. DLR safely prevents curtailment.")
elif live_loading > dynamic_rating:
    st.error("Even DLR cannot support this load. Curtailment required.")
else:
    st.info("Line operating safely within static limits.")

st.header("Economic Impact")

capacity_gain = dynamic_rating - static_rating
construction_saved = (capacity_gain / static_rating) * 200  # ₹200Cr baseline

st.metric("Estimated Construction Avoided (₹ Crore per 100km)", f"{construction_saved:.1f}")

st.header("Carbon Impact")

co2_saved = (capacity_gain / static_rating) * 0.9  # 0.9 MT per 10% unlock
st.metric("CO₂ Avoided (Million Tons/year)", f"{co2_saved:.2f}")

import plotly.graph_objects as go

st.markdown("## Thermal Utilization")

utilization = (live_loading / dynamic_rating) * 100

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=utilization,
    title={'text': "Line Utilization (%)"},
    gauge={
        'axis': {'range': [0, 150]},
        'bar': {'color': "darkred"},
        'steps': [
            {'range': [0, 80], 'color': "green"},
            {'range': [80, 100], 'color': "yellow"},
            {'range': [100, 150], 'color': "red"},
        ],
    }
))

st.plotly_chart(fig, use_container_width=True)

import plotly.express as px
import pandas as pd

st.markdown("## Static vs Dynamic Comparison")

df = pd.DataFrame({
    "Type": ["Static Rating", "Dynamic Rating", "Live Loading"],
    "Current (A)": [static_rating, dynamic_rating, live_loading]
})

fig2 = px.bar(df, x="Type", y="Current (A)", color="Type")

st.plotly_chart(fig2, use_container_width=True)



st.subheader("Interpretation")

if dynamic_rating > static_rating:
    st.success("DLR allows additional safe loading beyond static limits.")
else:
    st.warning("Weather conditions limit dynamic rating below static level.")