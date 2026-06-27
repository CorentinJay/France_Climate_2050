# 🌡️ France Climate 2050

URL : https://france-climate-2050.streamlit.app/ 

**France Climate 2050** est une application de data visualisation climatique qui projette l'évolution des températures et des extrêmes climatiques dans les principales villes françaises à l'horizon 2050.

---

## 🎯 Objectif

Face à l'accélération du réchauffement climatique, ce projet vise à rendre les données climatiques accessibles et parlantes pour tous — data scientists ou non. En partant de 75 ans de données historiques (1950-2026), l'application permet de visualiser :

- L'évolution des températures moyennes et maximales
- La fréquence croissante des jours de canicule (TX > 35°C)
- L'explosion des nuits tropicales (TN > 20°C)
- La température ressentie (Humidex)
- Des projections à horizon 2030, 2035, 2040, 2045 et 2050 selon trois scénarios (optimiste, médian, pessimiste)

---

## 📊 Source des données

### Stations Météo-France (source principale)
- **Source** : [meteo.data.gouv.fr](https://meteo.data.gouv.fr) — Données climatologiques de base quotidiennes
- **Variables** : TX (température maximale), TN (température minimale), TM (température moyenne)
- **Résolution** : mesures journalières au sol, stations officielles Météo-France
- **Période** : 1950 à 2026
- **Accès** : gratuit, licence ouverte Etalab
- **Avantage** : températures réelles mesurées au sol, sans lissage spatial

### ERA5-Land (Copernicus / ECMWF) — source complémentaire
- **Source** : [Copernicus Climate Data Store](https://cds.climate.copernicus.eu)
- **Variables utilisées** : point de rosée (`d2m`) pour le calcul de l'humidex uniquement
- **Résolution** : grille ~9 km, données horaires
- **Période** : 1950 à 2026
- **Accès** : gratuit via API Python `cdsapi`

### Calculs dérivés
- **Humidex** : température ressentie calculée selon la formule canadienne (Météo-France) à partir de TX station + point de rosée ERA5. Formule : `Humidex = T + 0.5555 × (e - 10)` où `e = 6.11 × exp(5417.75 × (1/273.16 - 1/(273.15 + Td)))`
- **Jours de canicule** : nombre de jours annuels avec TX > 35°C
- **Nuits tropicales** : nombre de nuits annuelles avec TN > 20°C

---

## 🏗️ Architecture

### Répertoires

**Back-end (local uniquement)**

    PROJET_CLIMATE_CHANGE/
    ├── data/
    │   ├── raw_full/          # Fichiers ERA5 bruts (~8 GB, non commités)
    │   ├── climate.db         # Base complète 781 900 lignes (~200 MB, non commitée)
    │   └── predictions.db     # Base légère exportée (~2 MB, commitée)
    ├── extraction/
    │   ├── 01_extract_era5.py        # Téléchargement ERA5 via cdsapi
    │   ├── 02_create_db.py           # Création de la base SQLite
    │   └── 03_parse_to_db_full.py    # Parsing NetCDF4 → SQLite + calcul heat index
    └── notebooks/
        ├── 01_exploration.ipynb      # Exploration et visualisation des données
        └── 02_modelisation.ipynb     # Modélisation et génération des projections

**Front-end (GitHub + Streamlit Cloud)**

    FranceClimate2050/
    ├── app.py              # Dashboard Streamlit
    ├── predictions.db      # Données pré-calculées (~2 MB)
    └── requirements.txt    # Dépendances Python

### Pipeline
1. **Extraction** : téléchargement des fichiers ERA5 année par année via `cdsapi` + extraction Meteo France API
2. **Parsing** : lecture des fichiers NetCDF4, extraction des points de grille les plus proches de chaque ville, agrégation journalière, calcul du heat index, insertion en base SQLite (`climate.db`)
3. **Modélisation** : régression polynomiale degré 2 avec bootstrap (1000 itérations) sur les agrégats annuels, génération des scénarios optimiste/médian/pessimiste pour chaque ville et chaque métrique
4. **Export** : sauvegarde des projections dans `predictions.db` (tables `predictions` et `historique`)
5. **Dashboard** : lecture de `predictions.db` et visualisation interactive via Streamlit

---

## 🛠️ Technologies utilisées

| Technologie | Usage |
|---|---|
| `Python` | Langage principal |
| `cdsapi` | Téléchargement des données ERA5 et Météo France |
| `xarray` | Lecture des fichiers NetCDF4 |
| `pandas` / `numpy` | Manipulation et agrégation des données |
| `SQLite` / `SQLAlchemy` | Stockage et requêtage des données |
| `scikit-learn` | Régression polynomiale + bootstrap |
| `Streamlit` | Dashboard interactif |
| `Plotly` | Visualisations interactives |

---

## 🧪 Technologies testées

Plusieurs approches de modélisation ont été explorées avant de retenir la régression polynomiale + bootstrap :

### Prophet (Facebook/Meta)
- **Avantage** : conçu pour les séries temporelles avec tendance et saisonnalité, intervalles de confiance natifs
- **Limite** : trop sensible au paramètre `changepoint_prior_scale` — résultats incohérents sur données climatiques longues
- **Verdict** : écarté

### Temporal Fusion Transformer (TFT)
- **Avantage** : état de l'art sur les séries temporelles multivariées, exploite le GPU (RTX 3080)
- **Limite** : conçu pour la prévision à court terme, surapprentissage inévitable pour des projections à 25 ans
- **Verdict** : écarté

### ERA5-Land comme source principale
- **Avantage** : couverture spatiale complète, données horaires
- **Limite** : grille de 9km qui lisse les températures — sous-estimation systématique des pics de +2 à +4°C par rapport aux stations au sol
- **Verdict** : remplacé par les stations Météo-France pour TX/TN, conservé uniquement pour le point de rosée

### Régression polynomiale + Bootstrap ✅
- **Avantage** : robuste, interprétable, adapté aux séries courtes (75 points annuels)
- **Les scénarios** optimiste/médian/pessimiste correspondent aux percentiles 10/50/90 des projections bootstrappées (1000 itérations)
- **Verdict** : retenu comme approche principale

---

## 🏙️ Villes couvertes (28)

Sélectionnées pour couvrir l'ensemble du territoire français avec des données de stations continues depuis 1950 et un taux de remplissage > 95% :

**Sud** : Avignon, Nîmes, Montpellier, Aix-en-Provence, Carcassonne, Toulouse, Mont-de-Marsan

**Sud-Ouest / Centre** : Bordeaux, Angoulême, Brive-la-Gaillarde, Limoges

**Centre / Ouest** : Poitiers, Bourges, Nantes, Le Mans, Rennes

**Nord / Est** : Paris, Lyon, Rouen, Amiens, Lille, Dijon, Strasbourg, Nancy

---

## ⚠️ Limites et précautions

- Les projections sont des **extrapolations statistiques** de tendances historiques observées, pas des simulations physiques de modèles climatiques globaux (GCM/CMIP6)
- L'intervalle optimiste/pessimiste reflète l'**incertitude statistique** du modèle, pas l'incertitude sur les scénarios d'émissions futures de CO₂
- L'humidex est calculé en combinant les températures stations (réelles) et le point de rosée ERA5 (grille 9km) — approximation acceptable compte tenu de la faible variabilité spatiale de l'humidité
- Certaines villes utilisent des **chaînages de stations** pour couvrir toute la période 1950-2026 (changements de station, fermetures)


*Données températures : Météo-France © — Licence Ouverte Etalab 2.0*
*Données point de rosée : ERA5-Land © Copernicus Climate Change Service (C3S) / ECMWF*