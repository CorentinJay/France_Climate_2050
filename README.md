# 🌡️ France Climate 2050

URL : https://france-climate-2050.streamlit.app/ 

**France Climate 2050** est une application de data visualisation climatique qui projette l'évolution des températures et des extrêmes climatiques dans les principales villes françaises à l'horizon 2050.

---

## 🎯 Objectif

Face à l'accélération du réchauffement climatique, ce projet vise à rendre les données climatiques accessibles et parlantes pour tous — data scientists ou non. En partant de 75 ans de données historiques (1950-2026), l'application permet de visualiser :

- L'évolution des températures moyennes et maximales
- La fréquence croissante des jours de canicule (t_max > 35°C)
- L'explosion des nuits tropicales (t_min > 20°C)
- La baisse tendancielle des précipitations
- Des projections à horizon 2030, 2035, 2040, 2045 et 2050 selon trois scénarios (optimiste, médian, pessimiste)

---

## 📊 Source des données

### ERA5-Land (Copernicus / ECMWF)
- **Source** : [Copernicus Climate Data Store](https://cds.climate.copernicus.eu)
- **Variables** : température à 2m (`t2m`), point de rosée à 2m (`d2m`), précipitations totales (`tp`)
- **Résolution** : grille ~10 km, 4 mesures par jour (06h, 12h, 15h, 18h)
- **Période** : 1950 à 2026
- **Accès** : gratuit via API Python `cdsapi`

### Calculs dérivés
- **Température ressentie (Heat Index)** : calculée à partir de la température et du point de rosée via la formule de Steadman, appliquée uniquement quand t > 27°C et humidité relative > 40%
- **Jours de canicule** : nombre de jours annuels avec t_max > 35°C
- **Nuits tropicales** : nombre de nuits annuelles avec t_min > 20°C

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
1. **Extraction** : téléchargement des fichiers ERA5 année par année via `cdsapi`
2. **Parsing** : lecture des fichiers NetCDF4, extraction des points de grille les plus proches de chaque ville, agrégation journalière, calcul du heat index, insertion en base SQLite (`climate.db`)
3. **Modélisation** : régression polynomiale degré 2 avec bootstrap (1000 itérations) sur les agrégats annuels, génération des scénarios optimiste/médian/pessimiste pour chaque ville et chaque métrique
4. **Export** : sauvegarde des projections dans `predictions.db` (tables `predictions` et `historique`)
5. **Dashboard** : lecture de `predictions.db` et visualisation interactive via Streamlit

---

## 🛠️ Technologies utilisées

| Technologie | Usage |
|---|---|
| `Python` | Langage principal |
| `cdsapi` | Téléchargement des données ERA5 |
| `xarray` | Lecture des fichiers NetCDF4 |
| `pandas` / `numpy` | Manipulation et agrégation des données |
| `SQLite` / `SQLAlchemy` | Stockage et requêtage des données |
| `scikit-learn` | Régression polynomiale + bootstrap |
| `Streamlit` | Dashboard interactif |
| `Plotly` | Visualisations interactives |

---

## 🧪 Technologies testées

Dans le cadre de ce projet, plusieurs approches de modélisation ont été explorées avant de retenir la régression polynomiale + bootstrap :

### Prophet (Facebook/Meta)
- **Avantage** : conçu pour les séries temporelles avec tendance et saisonnalité, intervalles de confiance natifs
- **Limite** : trop sensible au paramètre `changepoint_prior_scale` — trop conservateur il lisse excessivement, trop flexible il surfit sur les données récentes et génère des projections décroissantes incohérentes
- **Verdict** : écarté au profit d'une approche plus robuste sur des séries courtes (77 points annuels)

### Temporal Fusion Transformer (TFT)
- **Avantage** : état de l'art sur les séries temporelles multivariées, exploite le GPU (RTX 3080), gestion native de plusieurs séries simultanées
- **Limite** : conçu pour la prévision à court terme, pas pour l'extrapolation à 25 ans ; surapprentissage inévitable malgré l'entraînement multi-villes (20 séries × 918 points mensuels)
- **Verdict** : excellent outil pour la prévision météo à quelques mois, inadapté aux projections climatiques décennales sans données exogènes (CO₂, scénarios SSP)

### Régression polynomiale + Bootstrap ✅
- **Avantage** : robuste, interprétable, adapté aux séries courtes, génère naturellement un intervalle de confiance via bootstrap (1000 itérations)
- **Les scénarios** optimiste/médian/pessimiste correspondent aux percentiles 10/50/90 des projections bootstrappées
- **Verdict** : retenu comme approche principale

---

## 🏙️ Villes couvertes (28)

Sélectionnées pour couvrir l'ensemble du territoire français avec des données ERA5 fiables (points de grille terrestres, éloignés des zones côtières qui sont sous-estimées par ERA5-Land) :

**Sud** : Avignon, Nîmes, Montpellier, Aix-en-Provence, Carcassonne, Toulouse, Dax, Mont-de-Marsan

**Sud-Ouest / Centre** : Bordeaux, Angoulême, Brive-la-Gaillarde, Limoges, Clermont-Fd, Valence

**Centre / Ouest** : Poitiers, Bourges, Nantes, Le Mans, Rennes

**Nord / Est** : Paris, Rouen, Amiens, Reims, Lille, Dijon, Strasbourg, Nancy, Lyon

---

## ⚠️ Limites et précautions

- Les données ERA5-Land sous-estiment les températures dans les zones côtières (~2-4°C). Les villes littorales (Marseille, Nice, Toulon, Brest) ont été remplacées par des villes intérieures proches
- Les projections sont des extrapolations statistiques de tendances historiques, pas des simulations physiques de modèles climatiques globaux (GCM/CMIP6)
- L'intervalle optimiste/pessimiste reflète l'incertitude statistique du modèle, pas l'incertitude sur les scénarios d'émissions futurs


*Données : ERA5-Land © Copernicus Climate Change Service (C3S) / ECMWF*