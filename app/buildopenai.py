# app/streamlit_app.py

import os
import sys
import re
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Ensure sim_backend is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from sim_backend.ai_clientChat import run_trial  # Adjust import if your client module name differs

# ─── Helpers ─────────────────────────────────────────────────────────────────

def safe_parse_json(raw: str) -> dict:
    """
    Strip code fences and extra text, extract {...}, parse to dict.
    """
    cleaned = re.sub(r"^```(?:json)?\n", "", raw)
    cleaned = re.sub(r"\n```$", "", cleaned).strip()
    start = cleaned.find("{")
    end   = cleaned.rfind("}") + 1
    if start < 0 or end < 0:
        raise ValueError("No JSON object found in response")
    parsed = json.loads(cleaned[start:end])
    if not isinstance(parsed, dict):
        raise ValueError("Top‑level JSON is not an object")
    return parsed

def normalize_section(sec):
    """
    Ensure each section is a dict with 'value', 'explanation', and optional 'scaled_value'.
    """
    base = {"value": None, "explanation": "No explanation provided", "scaled_value": None}
    if isinstance(sec, dict):
        base["value"]        = sec.get("value")
        base["explanation"]  = sec.get("explanation") or base["explanation"]
        base["scaled_value"] = sec.get("scaled_value")
    elif isinstance(sec, str):
        base["value"] = sec
    return base

# ─── Streamlit Setup ─────────────────────────────────────────────────────────
load_dotenv()
st.set_page_config(page_title="In Silico Mouse Trial Simulator", layout="wide")
st.title("🔬 In Silico Mouse Trial Simulator")

# ─── Sidebar Inputs ──────────────────────────────────────────────────────────
st.sidebar.header("🛠 Trial Parameters")
with st.sidebar.form("params"):
    molecule_smiles = st.text_input(
        "SMILES",
        "COC1=C(C=C(C(N(CCN(C)C)C)=C1)NC(C=C)=O)NC2=NC=CC(C3=CN(C4=C3C=CC=C4)C)=N2"
    )
    strain          = st.text_input("Mouse strain", "C57BL/6")
    immune_state    = st.selectbox(
        "Immune state", ["immunocompetent", "immunodeficient", "humanized"]
    )
    genetic_mods    = st.text_area(
        "Genetic modifications (comma‑sep)", "p53 knockout"
    )
    disease_type    = st.text_input("Disease type", "lung cancer")
    disease_subtype = st.text_input("Disease subtype", "non‑small cell lung carcinoma")
    route           = st.selectbox("Administration route", ["oral", "iv", "ip", "sc"])
    dose            = st.number_input("Dose (mg/kg/day)", 50.0, step=1.0)
    duration_days   = st.number_input("Duration (days)", 14, step=1)
    run_button      = st.form_submit_button("▶️ Run Simulation")

if not run_button:
    st.write("Configure all parameters in the sidebar and click **Run Simulation**.")
    st.stop()

# ─── Build params & call AI ──────────────────────────────────────────────────
params = {
    "molecule_smiles": molecule_smiles,
    "mouse": {
        "strain":                strain,
        "immune_state":          immune_state,
        "genetic_modifications": [m.strip() for m in genetic_mods.split(",") if m.strip()],
    },
    "disease": {
        "type":    disease_type,
        "subtype": disease_subtype,
    },
    "administration": {
        "route":           route,
        "dose_mg_per_kg":  dose,
        "duration_days":   duration_days,
    }
}

with st.spinner("Running in silico trial…"):
    raw = run_trial(params)

# ─── Parse JSON ──────────────────────────────────────────────────────────────
try:
    result = safe_parse_json(raw)
except Exception as e:
    st.error(f"❌ Parsing error: {e}")
    st.code(raw, language="json")
    st.stop()

# ─── Section keys ────────────────────────────────────────────────────────────
KEY_TOX     = "1. Quantitative toxicity prediction"
KEY_MECH    = "2. Toxicity mechanism analysis"
KEY_EFFECTS = "3. Expected behavioral and physiological changes"
KEY_TEMP    = "4. Projected body temperature curve"
KEY_PATH    = "5. Pathway inhibition or activation"
KEY_AL      = "6. Activity loss evaluation"
KEY_IR      = "7. Immune response or gain-of-function profile"
KEY_OUT     = "trial_outcome"

# ─── Render in tabs ──────────────────────────────────────────────────────────
tabs = st.tabs([
    "🧪 Toxicity",
    "⚙️ Mechanistic Analysis",
    "🐁 Mouse Effects",
    "🌡️ Temperature Curve",
    "🧬 Pathway Inhibition",
    "🏃 Activity Loss",
    "🛡️ Immune Response",
    "🎯 Trial Outcome"
])

# 1) Toxicity
with tabs[0]:
    st.subheader("🧪 1. Quantitative Toxicity Prediction")
    tox = normalize_section(result.get(KEY_TOX, {}))
    st.metric(
        label="LD₅₀ / Toxicity",
        value=tox["value"],
        delta=(f"scaled {tox['scaled_value']}" if tox["scaled_value"] is not None else "")
    )
    st.write(tox["explanation"])

# 2) Mechanistic Analysis
with tabs[1]:
    st.subheader("⚙️ 2. Toxicity Mechanism Analysis")
    mech = normalize_section(result.get(KEY_MECH, {}))
    st.markdown(f"**Mechanism:**\n> {mech['value']}")
    st.markdown(f"**Explanation:**\n> {mech['explanation']}")

# 3) Mouse Effects
with tabs[2]:
    st.subheader("🐁 3. Expected Mouse Effects")
    eff = result.get(KEY_EFFECTS, {})
    metrics = [
        "locomotor_activity",
        "body_weight_change",
        "food_intake",
        "water_intake",
        "exploratory_behavior",
        "pain_threshold",
        "grooming_behavior"
    ]
    rows = []
    for m in metrics:
        if m in eff:
            sec = normalize_section(eff[m])
            rows.append({
                "Parameter": m.replace("_", " ").capitalize(),
                "Effect":    sec["value"]
            })
    if rows:
        st.table(pd.DataFrame(rows))
    else:
        st.info("No mouse‑effects data provided.")

# 4) Temperature Curve
with tabs[3]:
    st.subheader("🌡️ 4. Projected Body Temperature Curve")
    temp_sec = result.get(KEY_TEMP, {})
    if isinstance(temp_sec, dict) and temp_sec:
        days = list(temp_sec.keys())
        vals = [normalize_section(temp_sec[d])["value"] for d in days]
        fig  = go.Figure(go.Scatter(x=days, y=vals, mode="lines+markers"))
        fig.update_layout(xaxis_title="Day", yaxis_title="Temperature (°C)")
        st.plotly_chart(fig, use_container_width=True)
        for day in days:
            info = normalize_section(temp_sec[day])
            st.write(f"**{day}**: {info['value']} °C — {info['explanation']}")
    else:
        st.info("No temperature data provided.")

# 5) Pathway Inhibition
with tabs[4]:
    st.subheader("🧬 5. Pathway Inhibition or Activation")
    path_sec = result.get(KEY_PATH, {})
    rows = []
    for p, v in path_sec.items():
        sec = normalize_section(v)
        rows.append({
            "Pathway":     p,
            "Status":      sec["value"],
            "Explanation": sec["explanation"]
        })
    if rows:
        st.table(pd.DataFrame(rows))
    else:
        st.info("No pathway data provided.")

# 6) Activity Loss
with tabs[5]:
    st.subheader("🏃 6. Activity Loss Evaluation")
    al_sec = result.get(KEY_AL, {})
    rows = []
    for metric, v in al_sec.items():
        sec = normalize_section(v)
        rows.append({
            "Metric":      metric.replace("_", " ").capitalize(),
            "Value":       sec["value"],
            "Explanation": sec["explanation"]
        })
    if rows:
        df_al = pd.DataFrame(rows)
        try:
            st.bar_chart(df_al.set_index("Metric")["Value"])
        except:
            pass
        st.table(df_al)
    else:
        st.info("No activity‑loss data provided.")

# 7) Immune Response
with tabs[6]:
    st.subheader("🛡️ 7. Immune Response Profile")
    ir_sec = result.get(KEY_IR, {})
    rows = []
    for marker, v in ir_sec.items():
        sec = normalize_section(v)
        rows.append({
            "Marker":      marker,
            "Value":       sec["value"],
            "Explanation": sec["explanation"]
        })
    if rows:
        st.table(pd.DataFrame(rows))
    else:
        st.info("No immune response data provided.")

# 8) Trial Outcome + Download
with tabs[7]:
    st.subheader("🎯 8. Trial Outcome")
    out = result.get(KEY_OUT, {"result": "uncertain", "explanation": ""})
    if out["result"] == "pass":
        st.success("Result: PASS")
    elif out["result"] == "fail":
        st.error("Result: FAIL")
    else:
        st.warning("Result: UNCERTAIN")
    st.write(out["explanation"])
    st.download_button(
        "💾 Download Full JSON Report",
        data=json.dumps(result, indent=2),
        file_name="mouse_trial_report.json",
        mime="application/json"
    )
