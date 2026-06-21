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

# --- COORDONNÉES DES VILLES ---
COORDS = {
    "Paris":              (48.85,  2.35),
    "Lyon":               (45.75,  4.85),
    "Bordeaux":           (44.84, -0.58),
    "Toulouse":           (43.60,  1.44),
    "Nantes":             (47.22, -1.55),
    "Strasbourg":         (48.57,  7.75),
    "Lille":              (50.63,  3.07),
    "Montpellier":        (43.61,  3.87),
    "Rennes":             (48.11, -1.68),
    "Dijon":              (47.32,  5.04),
    "Reims":              (49.25,  4.03),
    "Angoulême":          (45.65,  0.16),
    "Clermont-Fd":        (45.78,  3.08),
    "Valence":            (44.93,  4.89),
    "Aix-en-Provence":    (43.53,  5.44),
    "Nîmes":              (43.84,  4.36),
    "Carcassonne":        (43.21,  2.35),
    "Dax":                (43.71, -1.05),
    "Mont-de-Marsan":     (43.89, -0.50),
    "Brive-la-Gaillarde": (45.15,  1.53),
    "Limoges":            (45.83,  1.26),
    "Poitiers":           (46.58,  0.34),
    "Le Mans":            (48.00,  0.20),
    "Rouen":              (49.44,  1.10),
    "Amiens":             (49.90,  2.30),
    "Nancy":              (48.69,  6.18),
    "Bourges":            (47.08,  2.40),
    "Avignon":            (43.95,  4.81),
}

# --- HELPERS ---
def get_metric(ville, metrique, year, col):
    val = predictions[
        (predictions['ville'] == ville) &
        (predictions['metrique'] == metrique) &
        (predictions['year'] == year)
    ][col].values
    return round(float(val[0]), 1) if len(val) > 0 else None

def get_serie(ville, metrique, col):
    return predictions[
        (predictions['ville'] == ville) &
        (predictions['metrique'] == metrique)
    ][['year', col]].rename(columns={col: 'value'})

def get_hist(ville, metrique):
    return historique[historique['ville'] == ville][['year', metrique]].rename(columns={metrique: 'value'})

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

# --- BLOC 1 : MÉTRIQUES CLÉS ---
st.subheader(f"📊 Indicateurs clés en {annee_cible}")

ref_year = 2024
col1, col2, col3, col4 = st.columns(4)

with col1:
    val = get_metric(ville, 't_mean', annee_cible, scenario_col)
    ref = get_metric(ville, 't_mean', ref_year, 'median')
    st.metric("🌡️ Température moyenne", f"{val}°C", f"{round(val-ref, 1):+}°C vs 2024")

with col2:
    val = get_metric(ville, 't_max', annee_cible, scenario_col)
    ref = get_metric(ville, 't_max', ref_year, 'median')
    st.metric("🔥 Température maximale", f"{val}°C", f"{round(val-ref, 1):+}°C vs 2024")

with col3:
    val = get_metric(ville, 'jours_canicule', annee_cible, scenario_col)
    ref = get_metric(ville, 'jours_canicule', ref_year, 'median')
    st.metric("☀️ Jours de canicule", f"{val} jours", f"{round(val-ref, 1):+} vs 2024")

with col4:
    val = get_metric(ville, 'nuits_tropicales', annee_cible, scenario_col)
    ref = get_metric(ville, 'nuits_tropicales', ref_year, 'median')
    st.metric("🌙 Nuits tropicales", f"{val} nuits", f"{round(val-ref, 1):+} vs 2024")

st.markdown("---")

# --- BLOC 2 & 3 : TEMPÉRATURE + JOURS CANICULE ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Température moyenne annuelle")
    hist_t = get_hist(ville, 't_mean')
    pred_opt = get_serie(ville, 't_mean', 'optimiste')
    pred_med = get_serie(ville, 't_mean', 'median')
    pred_pes = get_serie(ville, 't_mean', 'pessimiste')

    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=hist_t['year'], y=hist_t['value'], mode='markers',
        name='Observé', marker=dict(color='steelblue', size=5, opacity=0.6)))
    fig_t.add_trace(go.Scatter(x=pred_med['year'], y=pred_med['value'], mode='lines',
        name='Projection médiane', line=dict(color='red', width=2)))
    fig_t.add_trace(go.Scatter(x=pred_pes['year'], y=pred_pes['value'], mode='lines',
        line=dict(width=0), showlegend=False))
    fig_t.add_trace(go.Scatter(x=pred_opt['year'], y=pred_opt['value'], mode='lines',
        name='Intervalle', fill='tonexty', fillcolor='rgba(255,0,0,0.1)', line=dict(width=0)))
    fig_t.add_vline(x=2026, line_dash="dash", line_color="gray", annotation_text="Aujourd'hui")
    fig_t.add_vline(x=annee_cible, line_dash="dot", line_color="orange", annotation_text=str(annee_cible))
    fig_t.update_layout(height=500, xaxis_title="Année", yaxis_title="°C",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_t, use_container_width=True)

with col_right:
    st.subheader("🔥 Jours de canicule (t_max > 35°C)")
    hist_c = get_hist(ville, 'jours_canicule')
    pred_med_c = get_serie(ville, 'jours_canicule', 'median')
    pred_opt_c = get_serie(ville, 'jours_canicule', 'optimiste')
    pred_pes_c = get_serie(ville, 'jours_canicule', 'pessimiste')

    fig_c = go.Figure()
    fig_c.add_trace(go.Bar(x=hist_c['year'], y=hist_c['value'],
        name='Observé', marker_color='orangered', opacity=0.6))
    fig_c.add_trace(go.Scatter(x=pred_med_c['year'], y=pred_med_c['value'],
        mode='lines', name='Projection', line=dict(color='darkred', width=2)))
    fig_c.add_trace(go.Scatter(x=pred_pes_c['year'], y=pred_pes_c['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_c.add_trace(go.Scatter(x=pred_opt_c['year'], y=pred_opt_c['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(200,0,0,0.1)',
        line=dict(width=0), name='Intervalle'))
    fig_c.add_vline(x=2026, line_dash="dash", line_color="gray", annotation_text="Aujourd'hui")
    fig_c.add_vline(x=annee_cible, line_dash="dot", line_color="orange", annotation_text=str(annee_cible))
    fig_c.update_layout(height=500, xaxis_title="Année", yaxis_title="Jours",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_c, use_container_width=True)

st.markdown("---")

# --- BLOC 4 & 5 : NUITS TROPICALES + PRÉCIPITATIONS ---
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("🌙 Nuits tropicales (t_min > 20°C)")
    hist_n = get_hist(ville, 'nuits_tropicales')
    pred_med_n = get_serie(ville, 'nuits_tropicales', 'median')
    pred_opt_n = get_serie(ville, 'nuits_tropicales', 'optimiste')
    pred_pes_n = get_serie(ville, 'nuits_tropicales', 'pessimiste')

    fig_n = go.Figure()
    fig_n.add_trace(go.Bar(x=hist_n['year'], y=hist_n['value'],
        name='Observé', marker_color='purple', opacity=0.6))
    fig_n.add_trace(go.Scatter(x=pred_med_n['year'], y=pred_med_n['value'],
        mode='lines', name='Projection', line=dict(color='darkviolet', width=2)))
    fig_n.add_trace(go.Scatter(x=pred_pes_n['year'], y=pred_pes_n['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_n.add_trace(go.Scatter(x=pred_opt_n['year'], y=pred_opt_n['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(128,0,128,0.1)',
        line=dict(width=0), name='Intervalle'))
    fig_n.add_vline(x=2026, line_dash="dash", line_color="gray", annotation_text="Aujourd'hui")
    fig_n.add_vline(x=annee_cible, line_dash="dot", line_color="orange", annotation_text=str(annee_cible))
    fig_n.update_layout(height=500, xaxis_title="Année", yaxis_title="Nuits",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_n, use_container_width=True)

with col_right2:
    st.subheader("🌧️ Précipitations annuelles")
    hist_p = get_hist(ville, 'pr_sum')
    pred_med_p = get_serie(ville, 'pr_sum', 'median')
    pred_opt_p = get_serie(ville, 'pr_sum', 'optimiste')
    pred_pes_p = get_serie(ville, 'pr_sum', 'pessimiste')

    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=hist_p['year'], y=hist_p['value'],
        name='Observé', marker_color='steelblue', opacity=0.6))
    fig_p.add_trace(go.Scatter(x=pred_med_p['year'], y=pred_med_p['value'],
        mode='lines', name='Projection', line=dict(color='darkblue', width=2)))
    fig_p.add_trace(go.Scatter(x=pred_pes_p['year'], y=pred_pes_p['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_p.add_trace(go.Scatter(x=pred_opt_p['year'], y=pred_opt_p['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(0,0,200,0.1)',
        line=dict(width=0), name='Intervalle'))
    fig_p.add_vline(x=2026, line_dash="dash", line_color="gray", annotation_text="Aujourd'hui")
    fig_p.add_vline(x=annee_cible, line_dash="dot", line_color="orange", annotation_text=str(annee_cible))
    fig_p.update_layout(height=500, xaxis_title="Année", yaxis_title="mm",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_p, use_container_width=True)

st.markdown("---")



# --- BLOC 6 : TABLEAU COMPARATIF ---
st.subheader(f"📋 Comparatif toutes villes en {annee_cible}")

rows = []
for v in VILLES:
    rows.append({
        'Ville': v,
        'T. moyenne (°C)': get_metric(v, 't_mean', annee_cible, scenario_col),
        'T. max (°C)': get_metric(v, 't_max', annee_cible, scenario_col),
        'Jours canicule': get_metric(v, 'jours_canicule', annee_cible, scenario_col),
        'Nuits tropicales': get_metric(v, 'nuits_tropicales', annee_cible, scenario_col),
        'Précip. (mm)': get_metric(v, 'pr_sum', annee_cible, scenario_col),
    })

df_table = pd.DataFrame(rows).sort_values('T. moyenne (°C)', ascending=False).reset_index(drop=True)
st.dataframe(df_table, use_container_width=True, height=500)