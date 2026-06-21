import streamlit as st
import pandas as pd
import sqlalchemy as sa
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIG ---
st.set_page_config(
    page_title="France Climate 2050",
    page_icon="🌡️",
    layout="wide"
)

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    engine = sa.create_engine("sqlite:///predictions.db")
    predictions = pd.read_sql("SELECT * FROM predictions", engine)
    historique = pd.read_sql("SELECT * FROM historique", engine)
    return predictions, historique

predictions, historique = load_data()

VILLES = sorted(predictions['ville'].unique().tolist())

# --- SIDEBAR ---
st.sidebar.title("🌡️ France Climate 2050")
st.sidebar.markdown("---")

ville = st.sidebar.selectbox("Ville", VILLES, index=VILLES.index("Paris"))
annee_cible = st.sidebar.slider("Année cible", min_value=2030, max_value=2050, value=2040, step=5)
scenario = st.sidebar.radio("Scénario", ["Optimiste", "Médian", "Pessimiste"], index=1)

scenario_col = {"Optimiste": "optimiste", "Médian": "median", "Pessimiste": "pessimiste"}[scenario]

st.sidebar.markdown("---")
st.sidebar.markdown("*Données ERA5 — Copernicus/ECMWF*")
st.sidebar.markdown("*Modélisation : régression polynomiale + bootstrap*")

# --- TITRE ---
st.title(f"🌡️ Évolution climatique — {ville}")
st.markdown(f"Projections jusqu'en **{annee_cible}** — Scénario **{scenario}**")
st.markdown("---")

st.write("✅ App chargée avec succès")
st.write(f"Villes disponibles : {len(VILLES)}")