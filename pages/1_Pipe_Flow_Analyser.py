"""
1_Pipe_Flow_Analyser.py

Module A: Pipe Flow Analyser.

Lets the user pick a fluid (or define their own), enter pipe geometry and
flow rate, and see velocity / Reynolds number / friction factor / pressure
drop, plus a pressure-drop-vs-flow-rate curve. Results can be exported as
CSV.
"""

import streamlit as st
import pandas as pd

from engineering import Fluid, Pipe

st.set_page_config(page_title="Pipe Flow Analyser", page_icon="🌊", layout="wide")
st.title("🌊 Pipe Flow Analyser")
st.caption(
    "Calculates velocity, Reynolds number, Darcy friction factor, and "
    "pressure drop for steady, single-phase flow through a circular pipe "
    "using the Darcy-Weisbach equation."
)

# --------------------------------------------------------------------- #
# Sidebar inputs
# --------------------------------------------------------------------- #
st.sidebar.header("Fluid")

fluid_choice = st.sidebar.selectbox(
    "Fluid",
    options=list(Fluid.LIBRARY.keys()) + ["User-defined"],
    help="Pick a built-in fluid, or choose 'User-defined' to enter your own properties.",
)

if fluid_choice == "User-defined":
    density = st.sidebar.number_input(
        "Density (kg/m³)", min_value=0.0001, value=1000.0, step=10.0,
        help="Mass per unit volume of the fluid.",
    )
    viscosity = st.sidebar.number_input(
        "Dynamic viscosity (Pa·s)", min_value=0.0000001, value=1.0e-3,
        step=1.0e-4, format="%.6f",
        help="Resistance of the fluid to shearing flow. Water is about 0.001 Pa·s.",
    )
    fluid = Fluid(name="User-defined", density=density, viscosity=viscosity)
else:
    fluid = Fluid.from_library(fluid_choice)
    st.sidebar.write(f"Density: **{fluid.density} kg/m³**")
    st.sidebar.write(f"Viscosity: **{fluid.viscosity:.2e} Pa·s**")

st.sidebar.header("Pipe geometry")
diameter_mm = st.sidebar.number_input(
    "Internal diameter (mm)", min_value=1.0, value=50.0, step=5.0,
    help="Internal diameter of the pipe bore.",
)
length_m = st.sidebar.number_input(
    "Pipe length (m)", min_value=0.1, value=100.0, step=10.0,
    help="Total straight-line length of pipe the fluid travels through.",
)
roughness_mm = st.sidebar.number_input(
    "Absolute roughness (mm)", min_value=0.0, value=0.045, step=0.01,
    format="%.3f",
    help="Surface roughness of the pipe wall. ~0.045 mm is typical for "
         "commercial steel pipe; 0.0015 mm for drawn tubing/PVC.",
)

st.sidebar.header("Flow")
flow_rate_ls = st.sidebar.number_input(
    "Flow rate (L/s)", min_value=0.001, value=5.0, step=0.5,
    help="Volumetric flow rate through the pipe, in litres per second.",
)

# Convert to SI units
diameter_m = diameter_mm / 1000.0
roughness_m = roughness_mm / 1000.0
flow_rate_m3s = flow_rate_ls / 1000.0

pipe = Pipe(diameter=diameter_m, length=length_m, roughness=roughness_m)

# --------------------------------------------------------------------- #
# Results
# --------------------------------------------------------------------- #
try:
    fluid.validate()
    pipe.validate()
    results = pipe.full_report(fluid, flow_rate_m3s)

    st.subheader("Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Velocity", f"{results['velocity_m_s']:.3f} m/s")
    c2.metric("Reynolds number", f"{results['reynolds_number']:,.0f}")
    c3.metric("Friction factor", f"{results['friction_factor']:.4f}")
    c4.metric("Pressure drop", f"{results['pressure_drop_kpa']:.2f} kPa")

    st.write(f"Flow regime: **{results['flow_regime']}**")

    # ------------------------------------------------------------- #
    # Pressure drop vs flow rate curve
    # ------------------------------------------------------------- #
    st.subheader("Pressure drop vs flow rate")

    max_q = flow_rate_ls * 2 if flow_rate_ls > 0 else 10.0
    q_range_ls = [max_q * i / 49 for i in range(1, 50)]  # avoid Q=0
    dp_range_kpa = []
    for q_ls in q_range_ls:
        q_m3s = q_ls / 1000.0
        dp = pipe.pressure_drop(fluid, q_m3s) / 1000.0
        dp_range_kpa.append(dp)

    chart_df = pd.DataFrame({"Flow rate (L/s)": q_range_ls, "Pressure drop (kPa)": dp_range_kpa})
    st.line_chart(chart_df, x="Flow rate (L/s)", y="Pressure drop (kPa)")

    # ------------------------------------------------------------- #
    # Export
    # ------------------------------------------------------------- #
    st.subheader("Export")
    export_df = pd.DataFrame([{
        "Fluid": fluid.name,
        "Density (kg/m3)": fluid.density,
        "Viscosity (Pa.s)": fluid.viscosity,
        "Diameter (m)": diameter_m,
        "Length (m)": length_m,
        "Roughness (m)": roughness_m,
        "Flow rate (m3/s)": flow_rate_m3s,
        "Velocity (m/s)": results["velocity_m_s"],
        "Reynolds number": results["reynolds_number"],
        "Friction factor": results["friction_factor"],
        "Pressure drop (Pa)": results["pressure_drop_pa"],
        "Flow regime": results["flow_regime"],
    }])
    csv_bytes = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download results as CSV",
        data=csv_bytes,
        file_name="pipe_flow_results.csv",
        mime="text/csv",
    )
    st.dataframe(export_df, use_container_width=True)

except ValueError as e:
    st.error(f"Invalid input: {e}")
