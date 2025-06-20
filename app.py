import streamlit as st
import math
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Heat Exchanger Calculator", layout="centered")
st.title("🔧 Heat Exchanger Input Calculator")
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
    T_hot_out_known = st.checkbox("Input hot fluid outlet temp?")
    if T_hot_out_known:
        T_hot_out = st.number_input("Hot fluid outlet temp (°C)", value=50.0)
    else:
        T_hot_out = None

with col2:
    m_dot_cold = st.number_input("Cold fluid mass flow rate (kg/s)", min_value=0.0, value=1.0)
    Cp_cold = st.number_input("Cold fluid specific heat (kJ/kg·K)", min_value=0.0, value=4.18)
    T_cold_in = st.number_input("Cold fluid inlet temp (°C)", value=20.0)
    T_cold_out_known = st.checkbox("Input cold fluid outlet temp?")
    if T_cold_out_known:
        T_cold_out = st.number_input("Cold fluid outlet temp (°C)", value=45.0)
    else:
        T_cold_out = None

U = st.number_input("Overall heat transfer coefficient U (W/m²·K)", min_value=1.0, value=500.0)
flow_type = st.selectbox("Flow configuration", ["Counter-flow", "Parallel-flow"])

st.header("Results")

Q = None
T_hot_out_calc = None
T_cold_out_calc = None

if T_hot_out_known and T_cold_out_known:
    Q_hot = m_dot_hot * Cp_hot * (T_hot_in - T_hot_out) * 1000
    Q_cold = m_dot_cold * Cp_cold * (T_cold_out - T_cold_in) * 1000
    Q = min(Q_hot, Q_cold)
elif T_hot_out_known and not T_cold_out_known:
    Q = m_dot_hot * Cp_hot * (T_hot_in - T_hot_out) * 1000
    T_cold_out_calc = T_cold_in + Q / (m_dot_cold * Cp_cold * 1000)
elif not T_hot_out_known and T_cold_out_known:
    Q = m_dot_cold * Cp_cold * (T_cold_out - T_cold_in) * 1000
    T_hot_out_calc = T_hot_in - Q / (m_dot_hot * Cp_hot * 1000)
else:
    st.warning("Please provide at least three temperatures to perform the calculation.")

if Q is not None:
    if T_hot_out is None:
        T_hot_out = T_hot_out_calc
    if T_cold_out is None:
        T_cold_out = T_cold_out_calc

    # Validation
    valid_temp = True
    if T_hot_out >= T_hot_in:
        st.error("Hot fluid outlet temperature must be less than inlet temperature.")
        valid_temp = False
    if T_cold_out <= T_cold_in:
        st.error("Cold fluid outlet temperature must be greater than inlet temperature.")
        valid_temp = False

    if valid_temp:
        Q_hot = m_dot_hot * Cp_hot * (T_hot_in - T_hot_out) * 1000
        Q_cold = m_dot_cold * Cp_cold * (T_cold_out - T_cold_in) * 1000
        Q = min(Q_hot, Q_cold)

        if flow_type == "Counter-flow":
            delta_T1 = T_hot_in - T_cold_out
            delta_T2 = T_hot_out - T_cold_in
        else:
            delta_T1 = T_hot_in - T_cold_in
            delta_T2 = T_hot_out - T_cold_out

        if delta_T1 <= 0 or delta_T2 <= 0:
            LMTD = float('nan')
            st.error("Temperature difference(s) for LMTD are invalid (<= 0). Check your inlet and outlet temps.")
        elif delta_T1 == delta_T2:
            LMTD = delta_T1
        else:
            try:
                LMTD = (delta_T1 - delta_T2) / math.log(delta_T1 / delta_T2)
            except:
                LMTD = float('nan')
                st.error("Log mean temperature difference calculation failed.")

        if U > 0 and not math.isnan(LMTD):
            A = Q / (U * LMTD)
        else:
            A = float('nan')

        st.metric("Heat Duty (Q)", f"{Q/1000:.2f} kW")
        st.metric("LMTD", f"{LMTD:.2f} °C")
        st.metric("Required Area", f"{A:.2f} m²")

        # Temperature profile plot
        st.subheader("Temperature Profile")
        x = np.linspace(0, 1, 100)
        if flow_type == "Counter-flow":
            T_hot = T_hot_in - (T_hot_in - T_hot_out) * x
            T_cold = T_cold_out - (T_cold_out - T_cold_in) * (1 - x)
        else:
            T_hot = T_hot_in - (T_hot_in - T_hot_out) * x
            T_cold = T_cold_in + (T_cold_out - T_cold_in) * x

        fig, ax = plt.subplots()
        ax.plot(x, T_hot, label='Hot Fluid', linewidth=2)
        ax.plot(x, T_cold, label='Cold Fluid', linewidth=2, linestyle='--')
        ax.set_xlabel('Heat Exchanger Length (normalized)', fontsize=10)
        ax.set_ylabel('Temperature (°C)', fontsize=10)
        ax.set_title(f"{flow_type} Temperature Profile", fontsize=12, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend(loc='best', frameon=False)
        st.pyplot(fig)

with st.expander("Assumptions Used"):
    st.markdown("""
    - Fluids are well mixed and properties (Cp, density) are constant.
    - No phase change occurs in either stream.
    - Heat losses to the environment are negligible.
    - Flow is steady-state and 1D.
    - For plotting, linear temperature gradients are assumed.
    """)

st.caption("Built by Renuja Perera with Streamlit")
