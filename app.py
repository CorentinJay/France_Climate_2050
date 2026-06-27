import streamlit as st
import pandas as pd
import sqlalchemy as sa
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

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
    "Aix-en-Provence":    (43.53,  5.44),
    "Amiens":             (49.90,  2.30),
    "Angoulême":          (45.65,  0.16),
    "Avignon":            (43.95,  4.81),
    "Bordeaux":           (44.84, -0.58),
    "Bourges":            (47.08,  2.40),
    "Brive-la-Gaillarde": (45.15,  1.53),
    "Carcassonne":        (43.21,  2.35),
    "Dijon":              (47.32,  5.04),
    "Le Mans":            (48.00,  0.20),
    "Lille":              (50.63,  3.07),
    "Limoges":            (45.83,  1.26),
    "Lyon":               (45.75,  4.85),
    "Mont-de-Marsan":     (43.89, -0.50),
    "Montpellier":        (43.61,  3.87),
    "Nancy":              (48.69,  6.18),
    "Nantes":             (47.22, -1.55),
    "Nîmes":              (43.84,  4.36),
    "Paris":              (48.85,  2.35),
    "Poitiers":           (46.58,  0.34),
    "Rennes":             (48.11, -1.68),
    "Rouen":              (49.44,  1.10),
    "Strasbourg":         (48.57,  7.75),
    "Toulouse":           (43.60,  1.44),
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

def get_normale(ville, metrique):
    hist = get_hist(ville, metrique)
    return round(hist[(hist['year'] >= 1981) & (hist['year'] <= 2010)]['value'].mean(), 1)

def delta_str(val, ref):
    delta = round(val - ref, 1)
    pct = round((val - ref) / abs(ref) * 100, 1) if ref != 0 else 0
    return f"{delta:+} ({pct:+.1f}%)"

# --- SIDEBAR ---
st.sidebar.title("🌡️ France Climate 2050")
st.sidebar.markdown("---")
ville = st.sidebar.selectbox("Ville", VILLES, index=VILLES.index("Paris"))
annee_cible = st.sidebar.slider("Année cible", min_value=2030, max_value=2050, value=2040, step=5)
scenario = st.sidebar.radio("Scénario", ["Optimiste", "Médian", "Pessimiste"], index=1)
scenario_col = {"Optimiste": "optimiste", "Médian": "median", "Pessimiste": "pessimiste"}[scenario]
st.sidebar.markdown("---")
st.sidebar.markdown("*Données stations Météo-France*")
st.sidebar.markdown("*Modélisation : régression polynomiale + bootstrap*")

# --- TITRE ---
st.title(f"🌡️ Évolution climatique — {ville}")
st.markdown(f"Projections jusqu'en **{annee_cible}** — Scénario **{scenario}**")
st.markdown("---")

# --- BLOC 1 : MÉTRIQUES CLÉS ---
st.subheader(f"📊 Indicateurs clés en {annee_cible} vs normale 1981-2010")

col1, col2, col3, col4 = st.columns(4)

with col1:
    val = get_metric(ville, 'tm_mean', annee_cible, scenario_col)
    ref = get_normale(ville, 'tm_mean')
    st.metric("🌡️ Température moyenne", f"{val}°C", delta_str(val, ref) + "°C vs 1981-2010")

with col2:
    val = get_metric(ville, 'tx_max', annee_cible, scenario_col)
    ref = get_normale(ville, 'tx_max')
    st.metric("🔥 Température maximale", f"{val}°C", delta_str(val, ref) + "°C vs 1981-2010")

with col3:
    val = get_metric(ville, 'jours_canicule', annee_cible, scenario_col)
    ref = get_normale(ville, 'jours_canicule')
    ref = ref if ref > 0 else 0.1
    st.metric("☀️ Jours de canicule", f"{val} jours", delta_str(val, ref) + " vs 1981-2010")

with col4:
    val = get_metric(ville, 'nuits_tropicales', annee_cible, scenario_col)
    ref = get_normale(ville, 'nuits_tropicales')
    ref = ref if ref > 0 else 0.1
    st.metric("🌙 Nuits tropicales", f"{val} nuits", delta_str(val, ref) + " vs 1981-2010")

st.markdown("---")

# --- BLOC 2 & 3 : TEMPÉRATURE MOYENNE + JOURS CANICULE ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Température moyenne annuelle")
    hist_t = get_hist(ville, 'tm_mean')
    pred_opt = get_serie(ville, 'tm_mean', 'optimiste')
    pred_med = get_serie(ville, 'tm_mean', 'median')
    pred_pes = get_serie(ville, 'tm_mean', 'pessimiste')

    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=hist_t['year'], y=hist_t['value'], mode='markers',
        name='Observé', marker=dict(color='steelblue', size=5, opacity=0.6)))
    fig_t.add_trace(go.Scatter(x=pred_med['year'], y=pred_med['value'], mode='lines',
        name='Projection médiane', line=dict(color='red', width=2)))
    fig_t.add_trace(go.Scatter(x=pred_pes['year'], y=pred_pes['value'], mode='lines',
        line=dict(width=0), showlegend=False))
    fig_t.add_trace(go.Scatter(x=pred_opt['year'], y=pred_opt['value'], mode='lines',
        name='Intervalle', fill='tonexty', fillcolor='rgba(255,0,0,0.1)', line=dict(width=0)))
    fig_t.add_vline(x=2026, line_dash="dash", line_color="gray",
        annotation_text="Aujourd'hui", annotation_position="top left")
    fig_t.add_vline(x=annee_cible, line_dash="dot", line_color="orange",
        annotation_text=str(annee_cible), annotation_position="top right")
    fig_t.update_layout(height=500, xaxis_title="Année", yaxis_title="°C",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_t, use_container_width=True)

with col_right:
    st.subheader("🔥 Jours de canicule (Température > 35°C)")
    hist_c = get_hist(ville, 'jours_canicule')
    pred_med_c = get_serie(ville, 'jours_canicule', 'median')
    pred_opt_c = get_serie(ville, 'jours_canicule', 'optimiste')
    pred_pes_c = get_serie(ville, 'jours_canicule', 'pessimiste')

    hist_c_sorted = hist_c.sort_values('year')
    rolling_c = hist_c_sorted['value'].rolling(10, min_periods=5).mean()

    fig_c = go.Figure()
    fig_c.add_trace(go.Bar(x=hist_c_sorted['year'], y=hist_c_sorted['value'],
        name='Observé', marker_color='orangered', opacity=0.3))
    fig_c.add_trace(go.Scatter(x=hist_c_sorted['year'], y=rolling_c,
        mode='lines', name='Moyenne mobile 10 ans', line=dict(color='orangered', width=2)))
    fig_c.add_trace(go.Scatter(x=pred_med_c['year'], y=pred_med_c['value'],
        mode='lines', name='Projection', line=dict(color='darkred', width=2)))
    fig_c.add_trace(go.Scatter(x=pred_pes_c['year'], y=pred_pes_c['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_c.add_trace(go.Scatter(x=pred_opt_c['year'], y=pred_opt_c['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(200,0,0,0.1)',
        line=dict(width=0), name='Intervalle'))
    fig_c.add_vline(x=2026, line_dash="dash", line_color="gray",
        annotation_text="Aujourd'hui", annotation_position="top left")
    fig_c.add_vline(x=annee_cible, line_dash="dot", line_color="orange",
        annotation_text=str(annee_cible), annotation_position="top right")
    fig_c.update_layout(height=500, xaxis_title="Année", yaxis_title="Jours",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_c, use_container_width=True)

st.markdown("---")

# --- BLOC 4 & 5 : NUITS TROPICALES + HUMIDEX ---
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("🌙 Nuits tropicales (Temp. nocturne > 20°C)")
    hist_n = get_hist(ville, 'nuits_tropicales')
    pred_med_n = get_serie(ville, 'nuits_tropicales', 'median')
    pred_opt_n = get_serie(ville, 'nuits_tropicales', 'optimiste')
    pred_pes_n = get_serie(ville, 'nuits_tropicales', 'pessimiste')

    hist_n_sorted = hist_n.sort_values('year')
    rolling_n = hist_n_sorted['value'].rolling(10, min_periods=5).mean()

    fig_n = go.Figure()
    fig_n.add_trace(go.Bar(x=hist_n_sorted['year'], y=hist_n_sorted['value'],
        name='Observé', marker_color='purple', opacity=0.3))
    fig_n.add_trace(go.Scatter(x=hist_n_sorted['year'], y=rolling_n,
        mode='lines', name='Moyenne mobile 10 ans', line=dict(color='purple', width=2)))
    fig_n.add_trace(go.Scatter(x=pred_med_n['year'], y=pred_med_n['value'],
        mode='lines', name='Projection', line=dict(color='darkviolet', width=2)))
    fig_n.add_trace(go.Scatter(x=pred_pes_n['year'], y=pred_pes_n['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_n.add_trace(go.Scatter(x=pred_opt_n['year'], y=pred_opt_n['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(128,0,128,0.1)',
        line=dict(width=0), name='Intervalle'))
    fig_n.add_vline(x=2026, line_dash="dash", line_color="gray",
        annotation_text="Aujourd'hui", annotation_position="top left")
    fig_n.add_vline(x=annee_cible, line_dash="dot", line_color="orange",
        annotation_text=str(annee_cible), annotation_position="top right")
    fig_n.update_layout(height=500, xaxis_title="Année", yaxis_title="Nuits",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_n, use_container_width=True)

with col_right2:
    st.subheader("🥵 Température ressentie max (Humidex)")
    hist_h = get_hist(ville, 'humidex_max')
    pred_med_h = get_serie(ville, 'humidex_max', 'median')
    pred_opt_h = get_serie(ville, 'humidex_max', 'optimiste')
    pred_pes_h = get_serie(ville, 'humidex_max', 'pessimiste')

    hist_h_sorted = hist_h.sort_values('year')

    fig_h = go.Figure()
    fig_h.add_trace(go.Scatter(x=hist_h_sorted['year'], y=hist_h_sorted['value'], mode='markers',
        name='Observé', marker=dict(color='darkorange', size=5, opacity=0.6)))
    fig_h.add_trace(go.Scatter(x=pred_med_h['year'], y=pred_med_h['value'],
        mode='lines', name='Projection', line=dict(color='darkred', width=2)))
    fig_h.add_trace(go.Scatter(x=pred_pes_h['year'], y=pred_pes_h['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_h.add_trace(go.Scatter(x=pred_opt_h['year'], y=pred_opt_h['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(255,100,0,0.1)',
        line=dict(width=0), name='Intervalle'))
    fig_h.add_vline(x=2026, line_dash="dash", line_color="gray",
        annotation_text="Aujourd'hui", annotation_position="top left")
    fig_h.add_vline(x=annee_cible, line_dash="dot", line_color="orange",
        annotation_text=str(annee_cible), annotation_position="top right")
    fig_h.update_layout(height=500, xaxis_title="Année", yaxis_title="°C ressenti",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_h, use_container_width=True)

st.markdown("---")

# --- BLOC 6 : CARTE ---
st.subheader(f"🗺️ Carte des températures moyennes en {annee_cible}")

map_data = []
for v, (lat, lon) in COORDS.items():
    val = get_metric(v, 'tm_mean', annee_cible, scenario_col)
    if val:
        map_data.append({'ville': v, 'lat': lat, 'lon': lon, 'tx_mean': val})

df_map = pd.DataFrame(map_data)

fig_map = px.scatter_mapbox(
    df_map, lat='lat', lon='lon', color='tx_mean',
    size=[1] * len(df_map),
    size_max=15,
    hover_name='ville',
    hover_data={'tx_mean': ':.1f', 'lat': False, 'lon': False},
    color_continuous_scale='RdYlBu_r',
    range_color=[df_map['tx_mean'].min() - 1, df_map['tx_mean'].max() + 1],
    mapbox_style='carto-positron',
    zoom=5,
    center={"lat": 46.5, "lon": 2.5},
    labels={'tx_mean': '°C'},
)
fig_map.update_layout(
    height=600,
    coloraxis_colorbar=dict(title="°C"),
    margin=dict(l=0, r=0, t=0, b=0)
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# --- BLOC 7 : TABLEAU COMPARATIF ---
st.subheader(f"📋 Comparatif toutes villes en {annee_cible}")

rows = []
for v in VILLES:
    rows.append({
        'Ville': v,
        'T. moyenne (°C)': get_metric(v, 'tm_mean', annee_cible, scenario_col),
        'T. max (°C)': get_metric(v, 'tx_max', annee_cible, scenario_col),
        'Jours canicule': get_metric(v, 'jours_canicule', annee_cible, scenario_col),
        'Nuits tropicales': get_metric(v, 'nuits_tropicales', annee_cible, scenario_col),
        'Humidex max (°C)': get_metric(v, 'humidex_max', annee_cible, scenario_col),
    })

df_table = pd.DataFrame(rows).sort_values('T. moyenne (°C)', ascending=False).reset_index(drop=True)
st.dataframe(df_table, use_container_width=True, height=500)