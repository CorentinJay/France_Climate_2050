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

# --- TRADUCTIONS ---
TRANSLATIONS = {
    "fr": {
        "sidebar_title": "🌡️ France Climate 2050",
        "sidebar_ville": "Ville",
        "sidebar_annee": "Année cible",
        "sidebar_scenario": "Scénario",
        "sidebar_scenarios": ["Optimiste", "Médian", "Pessimiste"],
        "sidebar_data": "*Données stations Météo-France*",
        "sidebar_model": "*Modélisation : régression polynomiale + bootstrap*",
        "page_title": "Évolution climatique",
        "page_subtitle": "Projections jusqu'en",
        "page_scenario": "Scénario",
        "bloc1_title": "📊 Indicateurs clés en",
        "bloc1_vs": "vs normale 1981-2010",
        "metric_tm": "🌡️ Température moyenne",
        "metric_tx": "🔥 Température maximale",
        "metric_canicule": "☀️ Jours de canicule",
        "metric_nuits": "🌙 Nuits tropicales",
        "metric_unit_jours": "jours",
        "metric_unit_nuits": "nuits",
        "metric_vs": "vs 1981-2010",
        "graph_tm_title": "📈 Température moyenne annuelle",
        "graph_canicule_title": "🔥 Jours de canicule (Temp. max > 35°C)",
        "graph_nuits_title": "🌙 Nuits tropicales (Temp. nocturne > 20°C)",
        "graph_humidex_title": "🥵 Température ressentie max (Humidex)",
        "graph_observed": "Observé",
        "graph_median": "Projection médiane",
        "graph_interval": "Intervalle",
        "graph_projection": "Projection",
        "graph_rolling": "Moyenne mobile 10 ans",
        "graph_today": "Aujourd'hui",
        "graph_year": "Année",
        "graph_felt": "°C ressenti",
        "map_title": "🗺️ Carte climatique en",
        "map_delta": "**🌡️ Hausse température vs 1981-2010**",
        "map_canicule": "**☀️ Jours de canicule projetés**",
        "map_days": "jours",
        "table_title": "📋 Comparatif toutes villes en",
        "table_ville": "Ville",
        "table_tm": "T. moyenne (°C)",
        "table_tx": "T. max (°C)",
        "table_canicule": "Jours canicule",
        "table_nuits": "Nuits tropicales",
        "table_humidex": "Humidex max (°C)",
    },
    "en": {
        "sidebar_title": "🌡️ France Climate 2050",
        "sidebar_ville": "City",
        "sidebar_annee": "Target year",
        "sidebar_scenario": "Scenario",
        "sidebar_scenarios": ["Optimistic", "Median", "Pessimistic"],
        "sidebar_data": "*Data: Météo-France weather stations*",
        "sidebar_model": "*Model: polynomial regression + bootstrap*",
        "page_title": "Climate evolution",
        "page_subtitle": "Projections until",
        "page_scenario": "Scenario",
        "bloc1_title": "📊 Key indicators in",
        "bloc1_vs": "vs 1981-2010 baseline",
        "metric_tm": "🌡️ Average temperature",
        "metric_tx": "🔥 Maximum temperature",
        "metric_canicule": "☀️ Heatwave days",
        "metric_nuits": "🌙 Tropical nights",
        "metric_unit_jours": "days",
        "metric_unit_nuits": "nights",
        "metric_vs": "vs 1981-2010",
        "graph_tm_title": "📈 Annual average temperature",
        "graph_canicule_title": "🔥 Heatwave days (max temp. > 35°C)",
        "graph_nuits_title": "🌙 Tropical nights (night temp. > 20°C)",
        "graph_humidex_title": "🥵 Max feels-like temperature (Humidex)",
        "graph_observed": "Observed",
        "graph_median": "Median projection",
        "graph_interval": "Interval",
        "graph_projection": "Projection",
        "graph_rolling": "10-year moving average",
        "graph_today": "Today",
        "graph_year": "Year",
        "graph_felt": "°C feels like",
        "map_title": "🗺️ Climate map in",
        "map_delta": "**🌡️ Temperature rise vs 1981-2010**",
        "map_canicule": "**☀️ Projected heatwave days**",
        "map_days": "days",
        "table_title": "📋 All cities comparison in",
        "table_ville": "City",
        "table_tm": "Avg temp (°C)",
        "table_tx": "Max temp (°C)",
        "table_canicule": "Heatwave days",
        "table_nuits": "Tropical nights",
        "table_humidex": "Max Humidex (°C)",
    }
}

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

# --- SÉLECTEUR DE LANGUE (haut de page) ---
col_lang1, col_lang2 = st.columns([8, 1])
with col_lang2:
    col_fr, col_en = st.columns(2)
    with col_fr:
        if st.button("🇫🇷"):
            st.session_state['lang'] = 'fr'
    with col_en:
        if st.button("🇬🇧"):
            st.session_state['lang'] = 'en'

if 'lang' not in st.session_state:
    st.session_state['lang'] = 'fr'

lang = st.session_state['lang']
T = TRANSLATIONS[lang]

# --- SIDEBAR ---
st.sidebar.title(T["sidebar_title"])
st.sidebar.markdown("---")
ville = st.sidebar.selectbox(T["sidebar_ville"], VILLES, index=VILLES.index("Paris"))
annee_cible = st.sidebar.slider(T["sidebar_annee"], min_value=2030, max_value=2050, value=2040, step=5)
scenario = st.sidebar.radio(T["sidebar_scenario"], T["sidebar_scenarios"], index=1)
scenario_map = {s: c for s, c in zip(T["sidebar_scenarios"], ["optimiste", "median", "pessimiste"])}
scenario_col = scenario_map[scenario]
st.sidebar.markdown("---")
st.sidebar.markdown(T["sidebar_data"])
st.sidebar.markdown(T["sidebar_model"])

# --- TITRE ---
st.title(f"🌡️ {T['page_title']} — {ville}")
st.markdown(f"{T['page_subtitle']} **{annee_cible}** — {T['page_scenario']} **{scenario}**")
st.markdown("---")

# --- BLOC 1 : MÉTRIQUES CLÉS ---
st.subheader(f"{T['bloc1_title']} {annee_cible} {T['bloc1_vs']}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    val = get_metric(ville, 'tm_mean', annee_cible, scenario_col)
    ref = get_normale(ville, 'tm_mean')
    st.metric(T["metric_tm"], f"{val}°C", delta_str(val, ref) + f"°C {T['metric_vs']}")

with col2:
    val = get_metric(ville, 'tx_max', annee_cible, scenario_col)
    ref = get_normale(ville, 'tx_max')
    st.metric(T["metric_tx"], f"{val}°C", delta_str(val, ref) + f"°C {T['metric_vs']}")

with col3:
    val = get_metric(ville, 'jours_canicule', annee_cible, scenario_col)
    ref = get_normale(ville, 'jours_canicule')
    ref = ref if ref > 0 else 0.1
    st.metric(T["metric_canicule"], f"{val} {T['metric_unit_jours']}", delta_str(val, ref) + f" {T['metric_vs']}")

with col4:
    val = get_metric(ville, 'nuits_tropicales', annee_cible, scenario_col)
    ref = get_normale(ville, 'nuits_tropicales')
    ref = ref if ref > 0 else 0.1
    st.metric(T["metric_nuits"], f"{val} {T['metric_unit_nuits']}", delta_str(val, ref) + f" {T['metric_vs']}")

st.markdown("---")

# --- BLOC 2 & 3 : TEMPÉRATURE MOYENNE + JOURS CANICULE ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader(T["graph_tm_title"])
    hist_t = get_hist(ville, 'tm_mean')
    pred_opt = get_serie(ville, 'tm_mean', 'optimiste')
    pred_med = get_serie(ville, 'tm_mean', 'median')
    pred_pes = get_serie(ville, 'tm_mean', 'pessimiste')

    fig_t = go.Figure()
    fig_t.add_trace(go.Scatter(x=hist_t['year'], y=hist_t['value'], mode='markers',
        name=T["graph_observed"], marker=dict(color='steelblue', size=5, opacity=0.6)))
    fig_t.add_trace(go.Scatter(x=pred_med['year'], y=pred_med['value'], mode='lines',
        name=T["graph_median"], line=dict(color='red', width=2)))
    fig_t.add_trace(go.Scatter(x=pred_pes['year'], y=pred_pes['value'], mode='lines',
        line=dict(width=0), showlegend=False))
    fig_t.add_trace(go.Scatter(x=pred_opt['year'], y=pred_opt['value'], mode='lines',
        name=T["graph_interval"], fill='tonexty', fillcolor='rgba(255,0,0,0.1)', line=dict(width=0)))
    fig_t.add_vline(x=2026, line_dash="dash", line_color="gray",
        annotation_text=T["graph_today"], annotation_position="top left")
    fig_t.add_vline(x=annee_cible, line_dash="dot", line_color="orange",
        annotation_text=str(annee_cible), annotation_position="top right")
    fig_t.update_layout(height=500, xaxis_title=T["graph_year"], yaxis_title="°C",
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_t, use_container_width=True)

with col_right:
    st.subheader(T["graph_canicule_title"])
    hist_c = get_hist(ville, 'jours_canicule')
    pred_med_c = get_serie(ville, 'jours_canicule', 'median')
    pred_opt_c = get_serie(ville, 'jours_canicule', 'optimiste')
    pred_pes_c = get_serie(ville, 'jours_canicule', 'pessimiste')

    hist_c_sorted = hist_c.sort_values('year')
    rolling_c = hist_c_sorted['value'].rolling(10, min_periods=5).mean()

    fig_c = go.Figure()
    fig_c.add_trace(go.Bar(x=hist_c_sorted['year'], y=hist_c_sorted['value'],
        name=T["graph_observed"], marker_color='orangered', opacity=0.3))
    fig_c.add_trace(go.Scatter(x=hist_c_sorted['year'], y=rolling_c,
        mode='lines', name=T["graph_rolling"], line=dict(color='orangered', width=2)))
    fig_c.add_trace(go.Scatter(x=pred_med_c['year'], y=pred_med_c['value'],
        mode='lines', name=T["graph_projection"], line=dict(color='darkred', width=2)))
    fig_c.add_trace(go.Scatter(x=pred_pes_c['year'], y=pred_pes_c['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_c.add_trace(go.Scatter(x=pred_opt_c['year'], y=pred_opt_c['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(200,0,0,0.1)',
        line=dict(width=0), name=T["graph_interval"]))
    fig_c.add_vline(x=2026, line_dash="dash", line_color="gray",
        annotation_text=T["graph_today"], annotation_position="top left")
    fig_c.add_vline(x=annee_cible, line_dash="dot", line_color="orange",
        annotation_text=str(annee_cible), annotation_position="top right")
    fig_c.update_layout(height=500, xaxis_title=T["graph_year"], yaxis_title=T["metric_unit_jours"].capitalize(),
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_c, use_container_width=True)

st.markdown("---")

# --- BLOC 4 & 5 : NUITS TROPICALES + HUMIDEX ---
col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader(T["graph_nuits_title"])
    hist_n = get_hist(ville, 'nuits_tropicales')
    pred_med_n = get_serie(ville, 'nuits_tropicales', 'median')
    pred_opt_n = get_serie(ville, 'nuits_tropicales', 'optimiste')
    pred_pes_n = get_serie(ville, 'nuits_tropicales', 'pessimiste')

    hist_n_sorted = hist_n.sort_values('year')
    rolling_n = hist_n_sorted['value'].rolling(10, min_periods=5).mean()

    fig_n = go.Figure()
    fig_n.add_trace(go.Bar(x=hist_n_sorted['year'], y=hist_n_sorted['value'],
        name=T["graph_observed"], marker_color='purple', opacity=0.3))
    fig_n.add_trace(go.Scatter(x=hist_n_sorted['year'], y=rolling_n,
        mode='lines', name=T["graph_rolling"], line=dict(color='purple', width=2)))
    fig_n.add_trace(go.Scatter(x=pred_med_n['year'], y=pred_med_n['value'],
        mode='lines', name=T["graph_projection"], line=dict(color='darkviolet', width=2)))
    fig_n.add_trace(go.Scatter(x=pred_pes_n['year'], y=pred_pes_n['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_n.add_trace(go.Scatter(x=pred_opt_n['year'], y=pred_opt_n['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(128,0,128,0.1)',
        line=dict(width=0), name=T["graph_interval"]))
    fig_n.add_vline(x=2026, line_dash="dash", line_color="gray",
        annotation_text=T["graph_today"], annotation_position="top left")
    fig_n.add_vline(x=annee_cible, line_dash="dot", line_color="orange",
        annotation_text=str(annee_cible), annotation_position="top right")
    fig_n.update_layout(height=500, xaxis_title=T["graph_year"], yaxis_title=T["metric_unit_nuits"].capitalize(),
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_n, use_container_width=True)

with col_right2:
    st.subheader(T["graph_humidex_title"])
    hist_h = get_hist(ville, 'humidex_max')
    pred_med_h = get_serie(ville, 'humidex_max', 'median')
    pred_opt_h = get_serie(ville, 'humidex_max', 'optimiste')
    pred_pes_h = get_serie(ville, 'humidex_max', 'pessimiste')

    hist_h_sorted = hist_h.sort_values('year')

    fig_h = go.Figure()
    fig_h.add_trace(go.Scatter(x=hist_h_sorted['year'], y=hist_h_sorted['value'], mode='markers',
        name=T["graph_observed"], marker=dict(color='darkorange', size=5, opacity=0.6)))
    fig_h.add_trace(go.Scatter(x=pred_med_h['year'], y=pred_med_h['value'],
        mode='lines', name=T["graph_projection"], line=dict(color='darkred', width=2)))
    fig_h.add_trace(go.Scatter(x=pred_pes_h['year'], y=pred_pes_h['value'],
        mode='lines', line=dict(width=0), showlegend=False))
    fig_h.add_trace(go.Scatter(x=pred_opt_h['year'], y=pred_opt_h['value'],
        mode='lines', fill='tonexty', fillcolor='rgba(255,100,0,0.1)',
        line=dict(width=0), name=T["graph_interval"]))
    fig_h.add_vline(x=2026, line_dash="dash", line_color="gray",
        annotation_text=T["graph_today"], annotation_position="top left")
    fig_h.add_vline(x=annee_cible, line_dash="dot", line_color="orange",
        annotation_text=str(annee_cible), annotation_position="top right")
    fig_h.update_layout(height=500, xaxis_title=T["graph_year"], yaxis_title=T["graph_felt"],
        legend=dict(orientation="h", y=-0.15), hovermode="x unified")
    st.plotly_chart(fig_h, use_container_width=True)

st.markdown("---")

# --- BLOC 6 : CARTES ---
st.subheader(f"{T['map_title']} {annee_cible}")

col_map1, col_map2 = st.columns(2)

map_data = []
for v, (lat, lon) in COORDS.items():
    val_tm = get_metric(v, 'tm_mean', annee_cible, scenario_col)
    ref_tm = get_normale(v, 'tm_mean')
    val_canicule = get_metric(v, 'jours_canicule', annee_cible, scenario_col)
    if val_tm and ref_tm:
        map_data.append({
            'ville': v, 'lat': lat, 'lon': lon,
            'delta_tm': round(val_tm - ref_tm, 2),
            'jours_canicule': val_canicule
        })

df_map = pd.DataFrame(map_data)

with col_map1:
    st.markdown(T["map_delta"])
    fig_map1 = px.scatter_mapbox(
        df_map, lat='lat', lon='lon', color='delta_tm',
        size=[1] * len(df_map), size_max=15,
        hover_name='ville',
        hover_data={'delta_tm': ':.2f', 'lat': False, 'lon': False},
        color_continuous_scale='YlOrRd',
        range_color=[0, df_map['delta_tm'].max() + 0.5],
        mapbox_style='carto-positron',
        zoom=4.5, center={"lat": 46.5, "lon": 2.5},
        labels={'delta_tm': '°C'},
    )
    fig_map1.update_layout(height=500, coloraxis_colorbar=dict(title="°C"),
        margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map1, use_container_width=True)

with col_map2:
    st.markdown(T["map_canicule"])
    fig_map2 = px.scatter_mapbox(
        df_map, lat='lat', lon='lon', color='jours_canicule',
        size=[1] * len(df_map), size_max=15,
        hover_name='ville',
        hover_data={'jours_canicule': ':.1f', 'lat': False, 'lon': False},
        color_continuous_scale='YlOrRd',
        range_color=[0, df_map['jours_canicule'].max() + 1],
        mapbox_style='carto-positron',
        zoom=4.5, center={"lat": 46.5, "lon": 2.5},
        labels={'jours_canicule': T["map_days"]},
    )
    fig_map2.update_layout(height=500, coloraxis_colorbar=dict(title=T["map_days"].capitalize()),
        margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_map2, use_container_width=True)

st.markdown("---")

# --- BLOC 7 : TABLEAU COMPARATIF ---
st.subheader(f"{T['table_title']} {annee_cible}")

rows = []
for v in VILLES:
    rows.append({
        T["table_ville"]: v,
        T["table_tm"]: get_metric(v, 'tm_mean', annee_cible, scenario_col),
        T["table_tx"]: get_metric(v, 'tx_max', annee_cible, scenario_col),
        T["table_canicule"]: get_metric(v, 'jours_canicule', annee_cible, scenario_col),
        T["table_nuits"]: get_metric(v, 'nuits_tropicales', annee_cible, scenario_col),
        T["table_humidex"]: get_metric(v, 'humidex_max', annee_cible, scenario_col),
    })

df_table = pd.DataFrame(rows).sort_values(T["table_tm"], ascending=False).reset_index(drop=True)
st.dataframe(df_table, use_container_width=True, height=500)