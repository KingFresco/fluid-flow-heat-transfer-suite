"""
Home.py

Entry point for the Fluid Flow & Heat Transfer Engineering Suite.
Run with:  streamlit run Home.py
"""

import streamlit as st

st.set_page_config(
    page_title="Fluid Flow & Heat Transfer Suite",
    page_icon="🔧",
    layout="wide",
)

st.title("🔧 Fluid Flow & Heat Transfer Engineering Suite")

st.markdown(
    """
    Welcome! This app is a small toolkit for everyday fluid flow and heat
    transfer engineering calculations. Use the sidebar to navigate between
    modules:

    - **Pipe Flow Analyser** — velocity, Reynolds number, friction factor,
      and pressure drop for flow through a pipe.
    - **Heat Transfer Calculator** — steady-state conduction through a flat
      wall, and Newton's Law of Cooling for a body cooling in an ambient
      fluid.
    - **Rock & Fluid Data Dashboard** — upload a CSV of rock/fluid samples,
      filter it, and visualize porosity and permeability.

    All calculations are implemented in `engineering.py` as plain Python
    classes, independent of the Streamlit UI, so they can be tested and
    reused on their own.
    """
)

st.info(
    "Pick a module from the sidebar on the left to get started.",
    icon="👈",
)
