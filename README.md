# In_Virtual_Trials Simulator

A Streamlit‑based web app that uses an LLM (OpenAI GPT‑4o) to simulate preclinical mouse trials. Researchers enter molecular and biological parameters, and the system returns mechanistically grounded predictions—toxicity, mouse effects, temperature curves, pathway modulation, activity loss, immune profile—and a clear **pass / fail / uncertain** outcome.

---

## 🚀 Features

- **Intuitive UI**: Enter compound SMILES, dosing, mouse strain, immunostate, tumor model, etc.  
- **LLM‑powered Simulation**: GPT‑4o with a detailed system prompt for biologically realistic predictions.  
- **Seven Key Endpoints**:  
  1. Quantitative toxicity prediction  
  2. Mechanistic analysis  
  3. Behavioral & physiological changes  
  4. Body temperature curve  
  5. Pathway inhibition/activation  
  6. Activity loss metrics  
  7. Immune response profile  
- **Pass / Fail / Uncertain** trial outcome with clear rationale.  
- **Export JSON Report** of all predictions for downstream analysis.  

---

## 📋 Prerequisites

- **Python 3.9+**  
- **Streamlit**  
- **OpenAI API key** with GPT‑4o access  

---

## 🔧 Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-org/in_silico_mouse_trial.git
   cd in_silico_mouse_trial
