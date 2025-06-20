import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Heat Exchanger Calculator", layout="centered")
st.title("Heat Exchanger Input Calculator")
st.markdown("""
This tool calculates heat duty, log mean temperature difference (LMTD), and required heat exchanger area.
Supports **counter-flow** and **parallel-flow** exchangers.
""")

st.header("Input Parameters")
col1, col2 = st.columns(2)

with col1:
    m_dot_hot = st.number_input("Hot fluid mass flow rate (kg/s)", min_value=0.0, value=1.0)
    Cp_hot = st.number_input("Hot fluid specific heat (kJ/kg·K)", min_value=0.0, value=4.18)
    T_hot_in = st.number_input("Hot fluid inlet temp (°C)", value=80.0)
    T_hot_out = st.number_input("Hot fluid outlet temp (°C)", value=50.0)

with col2:
    m_dot_cold = st.number_input("Cold fluid mass flow rate (kg/s)", min_value=0.0, value=1.0)
    Cp_cold = st.number_input("Cold fluid specific heat (kJ/kg·K)", min_value=0.0, value=4.18)
    T_cold_in = st.number_input("Cold fluid inlet temp (°C)", value=20.0)
    T_cold_out = st.number_input("Cold fluid outlet temp (°C)", value=45.0)

U = st.number_input("Overall heat transfer coefficient U (W/m²·K)", min_value=1.0, value=500.0)
flow_type = st.selectbox("Flow configuration", ["Counter-flow", "Parallel-flow"])

# Validation of input parameters
Valid_temp = True
if T_hot_in <= T_hot_out:
    st.error("Hot fluid outlet temperature must be less than inlet temperature.")
    valid_temp = False
if T_cold_out <= T_cold_in:
    st.error("Cold fluid outlet temperature must be greater than inlet temperature.")
    valid_temp = False
if valid_temp:
    Q_hot = m_dot_hot * Cp_hot * (T_hot_in - T_hot_out) * 1000 # Heat duty(Q), Watts
    Q_cold = m_dot_cold * Cp_cold * (T_cold_out - T_cold_in) * 1000 # Watts
    Q = min(Q_hot, Q_cold)

    if flow_type == "Counter-flow": #LMTD 
        delta_T1 = T_hot_in - T_cold_out
        delta_T2 = T_hot_out - T_cold_in
    else: # Parallel Flow
        delta_T1 = T_hot_in - T_cold_in   
        delta_T2 = T_hot_out - T_cold_out

    if delta_T1 <= 0 or delta_T2 <= 0:
        LMTD = float ('nan')
        st.error("Temperature difference(s) for the LMTD are invalid (<=0). Check your inlet and outlet temperatures.")
    elif delta_T1 == delta_T2:
        LMTD = delta_T1
    else:
        try:
            LMTD = (delta_T1 - delta_T2) / math.log(delta_T1 / delta_T2)
        except:
            LMTD = float('nan')
            st.error("Log mean temperature difference calculation failed. Due to invalid inlet or outlet temperature values.")
    if U > 0 and not math.isnan(LMTD):
        A = Q / (U * LMTD)
    else:
        A = float('nan')

    st.header("Results")
    st.metric("Heat Duty (Q)", f"{Q/1000:.2f} kW")
    st.metric("LMTD", f"{LMTD:.2f} °C")
    st.metric("Required Area", f"{A:.2f} m²")
    
with st.expander("Assumptions Used"):
    st.markdown("""
    - Fluids are assumed to be well mixed and properties such as Cp and density are constant. 
    - No Phase change occurs for hot or cold streams.
    - Heat Losses to surroundings i.e through exchanger wall is negligible.
    - Flow is steady-state and 1D.
    - Linear temperature gradients are used for plotting. 
    """)
    # Temperature profile plot
    st.subheader("Temperature Profile")
    x = np.linspace(0, 1, 100)
    if flow_type == "Counter-flow":
        T_hot = T_hot_in - (T_hot_in - T_hot_out) * x
        T_cold = T_cold_out - (T_cold_out - T_cold_in) * (1 - x)
    else:
        T_hot = T_hot_in - (T_hot_in - T_hot_out) * x
        T_cold = T_cold_in + (T_cold_out - T_cold_in) * x

    figure, axes = plt.subplots()
    axes.plot(x, T_hot, label='Hot Fluid')
    axes.plot(x, T_cold, label='Cold Fluid')
    axes.set_xlabel('Heat Exchanger Length (normalized)')
    axes.set_ylabel('Temperature (°C)')
    axes.set_title(f"{flow_type} Temperature Profile")
    axes.legend()
    st.pyplot(figure)
st.caption("Built by Renuja Perera with Streamlit")
