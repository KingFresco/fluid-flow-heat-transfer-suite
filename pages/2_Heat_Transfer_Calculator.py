"""
2_Heat_Transfer_Calculator.py

Module B: Heat Transfer Calculator.

Two sub-tools:
  1. Steady-state conduction through a single-layer flat wall (Fourier's law).
  2. Newton's Law of Cooling: time to cool from T0 to a target temperature
     in an ambient fluid, plus a temperature-vs-time cooling curve.
"""

import streamlit as st
import pandas as pd

from engineering import HeatExchanger

st.set_page_config(page_title="Heat Transfer Calculator", page_icon="🔥", layout="wide")
st.title("🔥 Heat Transfer Calculator")

tab1, tab2 = st.tabs(["Steady-State Conduction", "Newton's Law of Cooling"])

# --------------------------------------------------------------------- #
# Tab 1: Conduction through a flat wall
# --------------------------------------------------------------------- #
with tab1:
    st.subheader("Steady-state conduction through a flat wall")
    st.caption(
        "Fourier's law for 1D steady conduction through a single homogeneous "
        "layer: heat flows from the hot face to the cold face at a rate "
        "q = k · A · ΔT / L."
    )

    col1, col2 = st.columns(2)
    with col1:
        k = st.number_input(
            "Thermal conductivity, k (W/m·K)", min_value=0.0001, value=0.8, step=0.1,
            help="Material property: how readily heat conducts through it. "
                 "Glass ≈ 0.8, steel ≈ 45, brick ≈ 0.7, insulation foam ≈ 0.03.",
        )
        area = st.number_input(
            "Cross-sectional area, A (m²)", min_value=0.0001, value=1.0, step=0.1,
            help="The area through which heat flows, perpendicular to the flow direction.",
        )
        thickness = st.number_input(
            "Wall thickness, L (m)", min_value=0.0001, value=0.01, step=0.005,
            format="%.4f",
            help="Distance the heat travels through the wall, from hot face to cold face.",
        )
    with col2:
        t_hot = st.number_input(
            "Hot-side temperature, T_hot (°C)", value=40.0, step=1.0,
            help="Temperature at the hot surface of the wall.",
        )
        t_cold = st.number_input(
            "Cold-side temperature, T_cold (°C)", value=20.0, step=1.0,
            help="Temperature at the cold surface of the wall.",
        )

    try:
        result = HeatExchanger.conduction_flat_wall(
            k=k, area=area, thickness=thickness, t_hot=t_hot, t_cold=t_cold
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Heat transfer rate", f"{result['heat_rate_w']:.2f} W")
        c2.metric("Heat flux", f"{result['heat_flux_w_m2']:.2f} W/m²")
        c3.metric("Thermal resistance", f"{result['thermal_resistance_k_w']:.5f} K/W")
    except ValueError as e:
        st.error(f"Invalid input: {e}")

# --------------------------------------------------------------------- #
# Tab 2: Newton's Law of Cooling
# --------------------------------------------------------------------- #
with tab2:
    st.subheader("Newton's Law of Cooling")
    st.caption(
        "Time for a (lumped) body to cool from an initial temperature T0 to "
        "a target temperature, in an ambient fluid at T_inf, given a "
        "convective heat transfer coefficient h and the body's surface area."
    )

    col1, col2 = st.columns(2)
    with col1:
        mass = st.number_input(
            "Mass, m (kg)", min_value=0.0001, value=1.0, step=0.1,
            help="Mass of the cooling body.",
        )
        cp = st.number_input(
            "Specific heat, c_p (J/kg·K)", min_value=0.0001, value=500.0, step=10.0,
            help="Energy needed to raise 1 kg of the material by 1 K. "
                 "Water ≈ 4186, steel ≈ 500, aluminium ≈ 900.",
        )
        h = st.number_input(
            "Convective coefficient, h (W/m²·K)", min_value=0.0001, value=10.0, step=1.0,
            help="How effectively the surrounding fluid carries heat away. "
                 "Still air ≈ 5-25, forced air ≈ 25-250, water ≈ 500-10000.",
        )
        surf_area = st.number_input(
            "Surface area, A (m²)", min_value=0.0001, value=0.1, step=0.01,
            help="Surface area of the body exposed to the ambient fluid.",
        )
    with col2:
        t0 = st.number_input(
            "Initial temperature, T0 (°C)", value=100.0, step=5.0,
            help="Starting temperature of the body.",
        )
        t_target = st.number_input(
            "Target temperature (°C)", value=40.0, step=5.0,
            help="Temperature you want the body to cool down to.",
        )
        t_inf = st.number_input(
            "Ambient temperature, T_inf (°C)", value=20.0, step=1.0,
            help="Temperature of the surrounding fluid, far from the body.",
        )

    try:
        cooling_seconds = HeatExchanger.cooling_time(
            mass=mass, specific_heat=cp, h=h, area=surf_area,
            t0=t0, t_target=t_target, t_inf=t_inf,
        )
        minutes = cooling_seconds / 60.0
        c1, c2 = st.columns(2)
        c1.metric("Time to cool", f"{cooling_seconds:.1f} s")
        c2.metric("Time to cool", f"{minutes:.2f} min")

        st.subheader("Cooling curve")
        # Show the curve out to ~1.5x the time to reach the target, for context.
        t_max = cooling_seconds * 1.5
        curve = HeatExchanger.cooling_curve(
            mass=mass, specific_heat=cp, h=h, area=surf_area,
            t0=t0, t_inf=t_inf, t_max=t_max, n_points=150,
        )
        curve_df = pd.DataFrame({
            "Time (s)": curve["time_s"],
            "Temperature (°C)": curve["temperature"],
        })
        st.line_chart(curve_df, x="Time (s)", y="Temperature (°C)")

    except ValueError as e:
        st.error(f"Invalid input: {e}")
