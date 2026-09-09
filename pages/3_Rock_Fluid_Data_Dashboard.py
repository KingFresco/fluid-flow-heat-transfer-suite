"""
3_Rock_Fluid_Data_Dashboard.py

Module C: Rock & Fluid Data Dashboard.

Lets the user upload a CSV of rock/fluid sample data, view summary
statistics, filter by porosity, view a porosity histogram and a
porosity-vs-permeability crossplot, and download the filtered data.
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rock & Fluid Data Dashboard", page_icon="🪨", layout="wide")
st.title("🪨 Rock & Fluid Data Dashboard")
st.caption(
    "Upload a CSV of rock or fluid sample data to see summary statistics, "
    "filter by porosity, and visualize porosity-permeability relationships."
)

st.info(
    "Expected columns: at minimum a **porosity** column (fraction or %) and "
    "a **permeability** column. Extra columns are fine and will just be "
    "carried through.",
    icon="ℹ️",
)

uploaded_file = st.file_uploader("Upload rock/fluid data CSV", type=["csv"])

# Small built-in sample so the page is usable even without a real dataset.
use_sample = st.checkbox("Use sample data instead", value=uploaded_file is None)

def load_sample_data() -> pd.DataFrame:
    """Return a small synthetic rock/fluid dataset for demo purposes."""
    import numpy as np
    rng = np.random.default_rng(42)
    n = 60
    porosity = rng.uniform(0.05, 0.30, n)
    # Rough porosity-permeability trend with scatter, in millidarcies
    permeability = (10 ** (porosity * 20 - 2)) * rng.uniform(0.5, 1.5, n)
    return pd.DataFrame({
        "sample_id": [f"S-{i+1:03d}" for i in range(n)],
        "porosity": porosity.round(4),
        "permeability_md": permeability.round(2),
    })

df = None
if uploaded_file is not None and not use_sample:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read the uploaded CSV: {e}")
elif use_sample:
    df = load_sample_data()
    st.caption("Showing sample data. Uncheck 'Use sample data' and upload a "
               "file to use your own.")

if df is not None:
    st.subheader("Data preview")
    st.dataframe(df, use_container_width=True)

    st.subheader("Summary statistics")
    st.dataframe(df.describe(), use_container_width=True)

    # Try to find a porosity-like column for filtering
    porosity_cols = [c for c in df.columns if "poro" in c.lower()]
    perm_cols = [c for c in df.columns if "perm" in c.lower()]

    if porosity_cols:
        poro_col = st.selectbox("Porosity column to filter on", porosity_cols)
        try:
            poro_series = pd.to_numeric(df[poro_col], errors="coerce")
            min_v, max_v = float(poro_series.min()), float(poro_series.max())
            threshold = st.slider(
                f"Show only samples where {poro_col} >",
                min_value=min_v, max_value=max_v, value=min_v,
                help="Filters the table and charts below to samples above this porosity value.",
            )
            filtered_df = df[poro_series > threshold]

            st.subheader(f"Filtered data ({len(filtered_df)} of {len(df)} samples)")
            st.dataframe(filtered_df, use_container_width=True)

            st.subheader("Charts")
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**{poro_col} histogram**")
                st.bar_chart(
                    pd.to_numeric(filtered_df[poro_col], errors="coerce").dropna(),
                )
            with c2:
                if perm_cols:
                    perm_col = st.selectbox("Permeability column for crossplot", perm_cols)
                    st.write(f"**{poro_col} vs {perm_col} crossplot**")
                    crossplot_df = filtered_df[[poro_col, perm_col]].apply(pd.to_numeric, errors="coerce").dropna()
                    st.scatter_chart(crossplot_df, x=poro_col, y=perm_col)
                else:
                    st.warning("No permeability-like column found for a crossplot.")

            st.subheader("Export")
            csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download filtered data as CSV",
                data=csv_bytes,
                file_name="filtered_rock_fluid_data.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Could not process porosity column '{poro_col}': {e}")
    else:
        st.warning("No column with 'poro' in its name was found, so filtering "
                    "and charts are unavailable for this file. Rename your "
                    "porosity column to include 'porosity' (or similar).")
else:
    st.write("Upload a CSV, or check 'Use sample data', to get started.")
