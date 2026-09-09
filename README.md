# Fluid Flow \& Heat Transfer Engineering Suite

A multi-page Streamlit application for everyday fluid flow and heat transfer
engineering calculations. Built as a course capstone project.

**Live app:** *https://fluid-flow-heat-transfer-suite-lbhqmpt7xeibmceuh9n2qb.streamlit.app*

## What it does

* **Pipe Flow Analyser** — pick a fluid (Water, Air, Crude Oil, or your own),
enter pipe geometry and flow rate, and see velocity, Reynolds number,
Darcy friction factor, and pressure drop (Darcy-Weisbach equation), plus
a pressure-drop-vs-flow-rate curve. Export results to CSV.
* **Heat Transfer Calculator** — steady-state 1D conduction through a flat
wall (Fourier's law), and Newton's Law of Cooling for a body cooling in
an ambient fluid, with a live cooling curve plot.
* **Rock \& Fluid Data Dashboard** — upload a CSV of rock/fluid sample data,
view summary statistics, filter by porosity, and view a porosity
histogram and porosity-permeability crossplot. Download the filtered
data as CSV.

## Project structure

```
fluid-flow-heat-transfer-suite/
├── Home.py                              # App entry point / landing page
├── engineering.py                       # OOP calculation classes (Fluid, Pipe, HeatExchanger)
├── pages/
│   ├── 1\_Pipe\_Flow\_Analyser.py
│   ├── 2\_Heat\_Transfer\_Calculator.py
│   └── 3\_Rock\_Fluid\_Data\_Dashboard.py
├── requirements.txt
└── README.md
```

All engineering calculations live in `engineering.py`, which has no
Streamlit code in it — it's plain Python (using dataclasses) that could be
imported and tested independently of the UI.

## Running locally

```bash
# 1. Create and activate a virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate      # on Windows: .venv\\Scripts\\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run Home.py
```

The app will open at http://localhost:8501.

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub (public).
2. Go to https://share.streamlit.io, sign in, and click "New app".
3. Point it at this repo, branch `main`, and main file `Home.py`.
4. Deploy — Streamlit Cloud will install `requirements.txt` automatically.

## Calculations \& references

* **Pipe flow**: Darcy-Weisbach equation for pressure drop; Swamee-Jain
explicit approximation to the Colebrook equation for the turbulent
friction factor (Re ≥ 2300), and f = 64/Re for laminar flow.
* **Conduction**: Fourier's law for steady 1D conduction through a single
homogeneous layer.
* **Cooling**: Newton's Law of Cooling under the lumped-capacitance
assumption (uniform temperature throughout the body).

## AI usage

*Fill in with your own 3 prompts, what you verified, and what you
corrected, as required by the assignment rubric.*

|#|Prompt (summary)|What I verified|What I corrected|
|-|-|-|-|
|1||||
|2||||
|3||||



