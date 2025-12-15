import streamlit as st
import requests
import os
import pandas as pd
import base64
import io
from PIL import Image

API_URL = "http://rakuten_predictor:8080"
RAW_DIR = os.path.join("data", "raw")
IMG_DIR = os.path.join(RAW_DIR, "images", "images")

st.set_page_config(layout="wide")

# =====================================================
#               SIDEBAR : MENU
# =====================================================

st.sidebar.title("Navigation du projet")

page = st.sidebar.radio(
    "Aller à :",
    [
        "1. Intro : contexte & objectifs",
        "2. Architecture globale / Dockerisation / Environnement développement",
        "3. Pipelines : train & predict + DB",
        "4. API",
        "5. Model Tracking : MLflow",
        "6. Automatisation : Airflow - drift / Evidently",
        "7. Monitoring : Grafana / Prometheus",
        "8. CI/CD : GitHub Actions",
        "9. Conclusion & Opportunités futures",
        "Démo : prédiction Rakuten",
    ],
)

# =====================================================
# 1. INTRO MARC
# =====================================================


if page == "1. Intro : contexte & objectifs":
    st.title("🎯 Introduction : Contexte & Objectifs du Projet")

    st.markdown("""
## 🧩 Contexte général

Ce projet s’inscrit dans le cadre du cursus **MLOps** et vise à transformer un modèle
de machine learning en une **application complète, industrialisable et maintenable**.

Le cas d’usage repose sur le challenge **Rakuten France Multimodal Product Classification**,
dont l’objectif est de prédire la catégorie produit (`prdtypecode`) à partir de :

- la **désignation** du produit  
- la **description textuelle**  
- **l’image du produit**

Ce problème est représentatif des besoins d’un e-commerce :  
recommandation, catégorisation automatique, qualité du catalogue, recherche intelligente.

---

## 🧠 Problématique à résoudre

- Comment **classifier automatiquement** des produits à partir d’informations multimodales ?
- Comment transformer un simple modèle ML en un **pipeline MLOps complet**, reproductible et déployable ?
- Comment garantir :
  - une **rapidité d’exécution** suffisante ?
  - une **traçabilité** des entraînements ?
  - une **mise en production** fiable ?
  - un **monitoring** et une détection de dérive ?
  - une **scalabilité** possible à l’avenir ?

---

## 🏢 Parties prenantes (Stakeholders)

### 👤 **Commanditaire**
- L'équipe technique du site e-commerce **Rakuten France**

### 👤 **Utilisateurs finaux**
- Les **administrateurs** de catégories Rakuten  
- Les équipes **catalogue** (contrôle qualité, modération)  
- Potentiellement : moteur interne de recherche / recommandation

### 👨‍💻 **Administrateurs de l’application**
- Équipe MLOps
- Data Engineers
- DevOps

---

## 🌍 Cadre d’intégration de l’application

- S’intègre dans un **système existant de gestion de catalogue**
- Déploiement prévu dans un environnement **Docker / Cloud**
- Interaction via :
  - **API FastAPI** (prédiction & authentification)
  - **Application Streamlit** (interface utilisateur)
  - **Pipeline Airflow** (entraînement automatisé)
  - **Monitoring Grafana / Prometheus**
  - **MLflow** pour le suivi des expériences & modèles

---

## 🎯 Objectifs du projet

- Construire un **pipeline complet** du preprocessing → entraînement → déploiement
- Assurer la **reproductibilité** via versioning du code, des données et des modèles
- Déployer un **modèle multimodal** performant (texte + image)
- Concevoir une **API** robuste + authentifiée
- Construire un **frontend Streamlit** simple & efficace
- Intégrer des pratiques MLOps :
  - CI/CD
  - Environnements Docker
  - MLflow Tracking & Registry
  - Monitoring
  - Orchestration Airflow

---

## 📅 Planning du projet (Phases)

### **📍 Phase 0 — Kick-off**
- Définition du périmètre  
- Documentation initiale  
- Cahier des charges  

---

### **📍 Phase 1 — Fondations**
- Mettre en place l’environnement reproductible  
- Collecte & pré-traitement des données  
- Base de données (MongoDB)  
- Modèle ML de base  
- Endpoints API : `/training` & `/predict`

---

### **📍 Phase 2 — Suivi & Versioning**
- Intégration MLflow Tracking  
- Versioning des modèles & données  
- Pipelines reproductibles  
- Comparaison automatique des versions

---

### **📍 Phase 3 — Déploiement & Orchestration**
- Découpage en microservices Docker  
- Orchestration via docker-compose  
- Pipeline CI/CD (GitHub Actions – optionnel)  
- Airflow pour l’entraînement planifié  

---

### **📍 Phase 4 — Monitoring & Maintenance**
- Monitoring GPU/CPU, latence API, ressources  
- Détection de dérive (Evidently AI)  
- Réentraînement automatisé  

---

### **📍 Phase 5 — Frontend**
- Développement d’une interface **Streamlit**  
- Interaction avec l’API  
- Visualisation des prédictions  

---

## 👥 Équipe projet

- **Clément**
- **Pascal**
- **Sébastien**
- **Marc**

---

💡 *Cette introduction sert de fil conducteur. Elle justifie les choix techniques et guide la progression MLOps tout au long du projet.*
""")
# =====================================================
# 2. ARCHITECTURE / DOCKER / ENV DE DEV SEBASTIEN
# =====================================================

elif page == "2. Architecture du projet":
    st.title("Architecture du projet")
    st.markdown("""
## 📂 Structure du Projet
```
    ├── .dockerignore      <- ignore for docker
    ├── .gitignore         <- ignore for git
    ├── .python-version    <- python version for uv
    ├── docker-compose-*.yml <- docker-compose for each components of the rakuten app (airflow, mongo, prometheus-grafana, etc.)
    ├── docker-compose.yml <- main docker-compose for rakuten app
    ├── LICENSE
    ├── Makefile           <- centralize command for docker components
    ├── pyproject.toml     <- The requirements file for reproducing the analysis environment
    ├── README.md          <- The top-level README for developers using this project.
    ├── uv.lock            <- UV file freezing dependances environnement
    ├── .github/workflows
    │   ├── ci.yml         <- Continuons Integration File for GitHub Actions
    │   └── cd.yml         <- Continuons Deployment File for GitHub Actions
    ├── conf               <- configuration files (mongo, prometheus, etc.)
    ├── data
    │   └── raw            <- The original, immutable data dump.
    ├── docker             <- Dockerfiles (api, airflow, mongo, etc.)
    ├── logs               <- Logs from app
    ├── models             <- Model save
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── evidently      <- Generated evidently reports
    ├── ressources         <- files for md files (images, graph, etc.)
    ├── src                <- Source code for use in this project.
    └── tests              <- tests files for CI
```

## 🛠️ Environnement de développement  

Gestion des dépendances Python avec `uv` et un fichier `pyproject.toml`, en utilisant des *extras* pour cibler finement les dépendances nécessaires à chaque conteneur Docker (API, training, Airflow, etc.).

Gestion de code source avec `git`, qualité de code assurée avec `ruff` pour le linting, le formatage et le respect des conventions PEP.

Utilisation de Docker pour développer et tester en local dans des conteneurs isolés, reliés via un réseau interne Docker Compose, ce qui rapproche fortement l’environnement de développement de l’environnement de déploiement.


## 🤖 Application métier ML/DL Rakuten

### Données et preprocessing

Les données brutes sont constituées d’un fichier CSV (descriptions texte + labels) et d’images stockées dans des sous-répertoires dédiés sous `/data/raw`.

Un job de preprocessing charge chaque jour une fraction du CSV (par exemple 1 000 lignes) et les images associées, nettoie et normalise le texte (TF‑IDF) ainsi que les images (features ResNet50), puis stocke les données prétraitées dans MongoDB.


### Entraînement

L’entraînement s’appuie exclusivement sur ces données propres (features texte + image) pour entraîner les modèles de classification de produits (ML/DL), avec suivi complet des expériences via MLflow.

MLflow enregistre les paramètres, métriques et artefacts des modèles, en s’appuyant sur PostgreSQL pour la métadonnée et MinIO comme stockage d’artefacts, ce qui permet d’identifier et de conserver automatiquement le meilleur modèle.


### Prédiction

La phase de prédiction sélectionne aléatoirement un exemple dans les données de test (texte + image) et récupère à la volée le meilleur modèle disponible auprès de MLflow pour produire une prédiction de catégorie.

L’API FastAPI expose des endpoints dédiés (`/train`, `/predict`) qui appellent respectivement les pipelines d’entraînement et de prédiction, ainsi qu’un endpoint `/login` qui gère l’authentification et délivre un token JWT exigé pour sécuriser les appels de train/predict.


## ⚙️ Outillage MLOps

### Orchestration des tâches

Airflow orchestre les jobs de preprocessing et d’entraînement quotidien, ainsi qu’un rapport de dérive via Evidently.
Si la dérive dépasse un seuil de 0,5, un réentraînement automatique est déclenché sur les dernières données propres.


### Monitoring et observabilité  

Prometheus collecte les métriques système (CPU, mémoire) et API, tandis que Grafana propose des dashboards dédiés pour visualiser l’état de la plateforme et la santé de l’API.


### Conteneurisation

Tous les composants (API FastAPI, jobs preprocessing/train/predict, MongoDB, MLflow, MinIO, PostgreSQL, Airflow, Prometheus, Grafana, Evidently) sont déployés dans des conteneurs Docker interconnectés, avec un volume monté pour `/data` et des volumes Docker spécifiques à chaque outil.


### Soutenance du projet

Streamlit sert d’interface utilisateur pour présenter le projet et permettre des tests en direct :
* L’application propose une sélection aléatoire de 5 couples texte/image issus du jeu de test.
* Elle interroge l’API de prédiction pour afficher la catégorie estimée et les informations associées.

""")

# =====================================================
# 3. PIPELINES TRAIN & PREDICT + DB MARC
# =====================================================


elif page == "3. Pipelines : train & predict + DB":
    st.title("🔁 Pipelines : Train, Predict & Base de Données")

    st.markdown("""
## 🎯 Objectif général
Mettre en place un pipeline complet texte + image, depuis le nettoyage des données
jusqu'à l'entraînement du modèle XGBoost, en s'appuyant sur une base de données MongoDB
comme source unique de données nettoyées.

---

# 🧹 1️⃣ CLEANING PIPELINE (clean_data.py)

📥 Données entrantes :
- X_train_update.csv, Y_train_CVw08PX.csv
- X_test_update.csv
- Images produit (train / test)

🔧 Nettoyage :
- Suppression HTML (BeautifulSoup)
- Normalisation accents, ponctuation, caractères spéciaux
- Mise en minuscule, regex, trimming
- Images : resize 224×224, conversion en JPEG, stockage en bytes

🗄️ Insertion dans MongoDB :
- Collection X_train_cleaned
- Collection X_test_cleaned

Contenu typique d'un document :
- id
- designation nettoyée
- description nettoyée
- prdtypecode
- image_binary (JPEG en binaire)

MongoDB devient la source unique de vérité pour le pipeline ML.

---

# 🧠 2️⃣ PREPROCESSING PIPELINE (preprocess_data.py)

TF-IDF (texte) :
- 20 000 features
- unigrammes + bigrammes
- min_df = 2

Embeddings images (ResNet50) :
- Chargement ResNet50
- Extraction embeddings 2048-D
- Normalisation ImageNet
- Traitement par batch

Fusion des données :
- concaténation sparse : [ TF-IDF | embeddings image ]
- production de X_train_full et X_val_full

---

# 🚀 3️⃣ TRAIN PIPELINE (train.py)

Modèle XGBoost :
- objective = multi:softprob
- tree_method = hist
- max_depth = 8

Entraînement :
- Split train / validation (stratifié)
- Encodage des labels avec LabelEncoder
- Suivi de l'entraînement avec tqdm

Évaluation :
- Accuracy
- F1 score pondéré
- Rapport de classification

Artefacts sauvegardés :
- xgb_fusion.json (modèle)
- label_encoder.joblib
- tfidf_vectorizer.joblib
- fichier de métriques (accuracy, F1)

---

# 📊 4️⃣ Tracking MLflow

MLflow enregistre :
- paramètres du modèle
- métriques (accuracy, F1)
- artefacts (modèle, TF-IDF, encodeur)
- historique des différentes versions

Backend de stockage : MinIO (bucket mlflow-artifacts).

---

# 🗄️ 5️⃣ BASE DE DONNÉES : MongoDB

Pourquoi MongoDB ?
- Gère facilement texte + image binaire
- Modèle flexible adapté aux données multimodales
- Centralise les données nettoyées
- Facilite la reproductibilité du pipeline

Rôle dans le pipeline :
- clean_data.py lit les CSV / images brutes, nettoie et insère dans X_train_cleaned et X_test_cleaned
- preprocess_data.py lit directement ces collections pour reconstruire :
  - le texte concaténé (designation + description)
  - les images à partir de image_binary
  - les features TF-IDF + ResNet50
- l'API de prédiction peut ensuite interroger MongoDB pour récupérer des produits à prédire

Scripts associés :
- conf_loader.py : charge la configuration MongoDB (YAML + valeurs par défaut)
- utils.py (MongoUtils) : fournit un context manager pour se connecter proprement à MongoDB
- setup_database.py : crée des index, insère des données de test et valide le setup

---

# 🔁 Schéma global du pipeline
    """)

    st.graphviz_chart(
        """
digraph {
    rankdir=LR;
    node [shape=box, style="rounded,filled", color="#1E88E5", fontcolor=white, fontsize=18];

    A [label="CSV + Images\nDonnées brutes"];
    B [label="Cleaning texte + image\n(clean_data.py)"];
    BB [label="MongoDB\nX_train_cleaned\nX_test_cleaned"];
    C [label="Préprocessing\nTF-IDF + ResNet50\n(preprocess_data.py)"];
    D [label="Fusion sparse\n(texte + image)"];
    E [label="Train XGBoost\n(train.py)"];
    F [label="MLflow Tracking\nMetrics + Artefacts"];

    A -> B -> BB -> C -> D -> E -> F;
}
""",
        width="stretch",
    )


# =====================================================
# 4. API
# =====================================================

elif page == "4. API":
    st.title("API")
    st.markdown("""L’API Rakuten est composée de deux services principaux :
- Un service de prédiction
- Un service d’entraînement du modèle
Ces deux services sont organisés sous forme d’API FastAPI distinctes, mais qui fonctionnent selon une logique similaire.""")
    st.write("### Gestion Login et token")
    st.markdown("""Les deux services utilisent un mécanisme d’authentification par token JWT.
Le fonctionnement est le suivant :
- L’utilisateur doit appeler l’endpoint /login en fournissant un identifiant et un mot de passe.
- Si les identifiants sont valides, l’API renvoie un token JWT valable pendant 1 heure.
- Toutes les requêtes aux endpoints sensibles (/predict ou /train) doivent inclure ce token dans l’entête Authorization: Bearer <token>.
Si le token est absent, invalide ou expiré, l’accès est refusé.
""")
    st.write("### Gestion de l'entrainement")
    st.markdown("""Le service d’entraînement propose un endpoint : /train.
Fonctionnement général
Après authentification :
L’API appelle le module d’entraînement du modèle.
Le modèle est réentraîné selon les procédures définies dans ce module externe.
L’API retourne un message indiquant que l’authentification est correcte, que l’entraînement s’est bein effectué et que les données retournées par le processus d’entraînement.
En cas d’erreur ou d’absence de token valide, une erreur est renvoyée.
""")
    st.write("### Gestion de la prediction")
    st.markdown("""Le service de prédiction offre un endpoint principal : /predict.
Fonctionnement général
Lors d’un appel à ce service authentifié :
- L’API sélectionne au hasard une ligne dans un fichier CSV contenant des données de test.
- Elle identifie l’image correspondante à cette ligne dans un dossier d’images.
- Elle charge :l’image du produit, la désignation, la description.
- Elle envoie ces données au module de prédiction du modèle machine learning.
- L’API retourne : le résultat de la prédiction, la désignation et la description utilisées, un message indiquant que la connexion et la prédiction ont réussi.
Si l’image n’existe pas, l’API renvoie un message indiquant qu’aucun résultat n’est disponible.
""")
    st.write("### Gestion de la vérification et du monitoring")
    st.markdown("""Chaque service expose également un endpoint / (POST) qui renvoie simplement un message confirmant que l’API est opérationnelle.
Cela permet de vérifier rapidement l’état du service.

Les deux API sont instrumentées avec Prometheus via prometheus_fastapi_instrumentator.
Cela permet d’exposer des métriques lié à l'api, de monitorer les performances, d’analyser les requêtes.
""")
    st.write("### Test unitaire")
    st.markdown("""Les tests unitaires réaliser permettent de valider le fonctionnement général de l’API Rakuten, en se concentrant sur trois aspects essentiels :
- La gestion de l’authentification
- Le comportement de l’API de prédiction
- Le comportement de l’API d’entraînement du modèle
Ils effectuent ces vérifications sur les deux api présenté précédemment :
- l’API d’entraînement (port 8000)
- l’API de prédiction (port 8080)
La première série de test confirme le bon fonctionnement de la génération du token et de sa validation pour l'authentification.
Les autres tests sont la vérification du fonctionnement des endpoints /train et /predict avec un token correct et incorrect.
""")


# =====================================================
# 5. MLflow PASCAL
# =====================================================

elif page == "5. Model Tracking : MLflow":
    st.title("Model Tracking : MLflow")

    st.markdown("""
### 🎯 Rôle de MLflow dans le projet

MLflow est utilisé comme **serveur central de suivi des expériences** :
- Suivi des runs d'entraînement (un run = une exécution du script `train.py`)
- Journalisation des **paramètres / hyperparamètres** du modèle XGBoost
- Suivi des **métriques** (accuracy, F1, etc.)
- Stockage des **artefacts** : modèle, TF-IDF, LabelEncoder, logs...
[web:35][web:81][web:86]
    """)

    st.markdown("""
### 🏗️ Infrastructure MLflow (Docker + MinIO)

- Service **MLflow** dans un conteneur dédié (port 5000) avec backend SQLite pour les métadonnées des runs
- Service **MinIO (S3)** pour stocker les artefacts dans le bucket `mlflow-artifacts`
- Variables d'environnement (`MLFLOW_HOST`, `MLFLOW_S3_ENDPOINT_URL`, clés MinIO) pour connecter les scripts au tracking server
[web:1][web:10][web:16][web:89]
    """)

    st.markdown("""
### 🧪 Tracking côté entraînement (`train.py`)

- Le script `train()` initialise l'expérience `rakuten_xgb_fusion` et démarre un **run MLflow**
- Log des hyperparamètres XGBoost (profondeur, learning rate, device CPU/GPU...)
- Log des métriques de validation (accuracy, F1) et du modèle XGBoost + artefacts de prétraitement (TF-IDF, LabelEncoder)
[web:21][web:22][web:26][web:82]
    """)

    st.markdown("""
### 🔮 Tracking côté prédiction (`predict.py`)

- L'API de prédiction interroge MLflow pour récupérer le **meilleur run** de l'expérience (trié par accuracy)
- Chargement du modèle (`runs:/<run_id>/xgb_model`) et des artefacts associés depuis le store d'artefacts (MinIO)
- L'endpoint de prédiction sert toujours le modèle le plus performant enregistré dans MLflow
[web:35][web:40][web:45][web:90]
    """)

    st.markdown("""
### 🌐 Intégration avec l'API

- Endpoint `/train` → déclenche `train()` et crée un nouveau run MLflow
- Endpoint `/predict` → appelle `predict()`, recharge le meilleur modèle depuis MLflow et renvoie une prédiction JSON
- Séparation claire entre **tracking des expériences** (MLflow) et **serving** (API + Streamlit)
[web:59][web:62][web:71][web:83]
    """)


# =====================================================
# 6. AIRFLOW + DRIFT
# =====================================================

elif page == "6. Automatisation : Airflow - drift / Evidently":
    st.title("🌀 Automatisation : Airflow")

    st.markdown("""
### 🏗️ Infrastructure Airflow (Docker)

Airflow est déployé dans un cluster Docker avec :
- Une base **PostgreSQL** pour la métabase Airflow.
- Un broker **Redis** pour Celery.
- Trois services Airflow : **webserver**, **scheduler** et **worker**, tous en **CeleryExecutor**.
- Un conteneur **airflow-init** pour initialiser la base et créer l'utilisateur web.
    """)

    st.markdown("""
### 📡 DAG de monitoring de dérive (Evidently)

**DAG : `rakuten_data_drift_monitoring` (tous les jours à 8h)**

- Charge un échantillon **référence** et **courant** du fichier `X_train_update.csv` en fonction des dates.
- Nettoie uniquement le texte (`designation`, `description`) puis construit `title_clean` et `description_clean`.
- Utilise Evidently pour calculer :
  - `DatasetDriftMetric` sur l'ensemble du dataset.
  - `ColumnDriftMetric` sur `title_clean` et `description_clean` (avec un seuil de test statistique).
  - `TextDescriptorsDriftMetric` sur les deux colonnes texte.

Le DAG :
- Sauvegarde un **rapport HTML** de dérive dans `/app/reports/evidently_reports/`.
- Combine les flags de drift pour décider s'il y a un **drift global**.
- Utilise un `BranchPythonOperator` pour choisir entre :
  - déclencher le DAG d'entraînement (`trigger_rakuten_weekly_training`),
  - ou ne rien faire (`no_trigger`).
[web:131][web:132][web:138][web:148]
    """)

    st.markdown("""
### 🔁 DAG d'entraînement hebdomadaire

**DAG : `rakuten_weekly_training` (tous les lundis à 4h)**

- Tâche `get_token_task` :
  - Appelle l'endpoint `/login` du service **trainer** (FastAPI) pour récupérer un jeton d'authentification.
- Tâche `call_api_task` :
  - Appelle l'endpoint `/train` du service **trainer` avec ce jeton.
  - Déclenche l'entraînement du modèle Rakuten dans le conteneur `trainer` (qui logue ensuite le run dans MLflow).

Ce DAG peut être lancé :
- automatiquement chaque semaine par le scheduler,
- ou **à la demande** par le DAG de dérive lorsqu'un drift est détecté.
[web:94][web:129][web:111]
    """)

    st.markdown("""
### 🧠 Rôle d'Airflow dans la pipeline

Airflow joue le rôle de **chef d'orchestre** de la pipeline MLOps :
- Surveille la **dérive des données texte** au quotidien avec Evidently.
- **Automatise** le déclenchement de l'entraînement via l'API `trainer`.
- Centralise la **traçabilité** des exécutions (états des DAGs, logs, durées) dans l'UI Airflow.

Il relie ainsi la partie **données** (drift) et la partie **modèle** (ré-entraînement + tracking MLflow) dans un même outil d'orchestration.
[web:103][web:111][web:112]
    """)

# =====================================================
# 7. MONITORING
# =====================================================

elif page == "7. Monitoring : Grafana / Prometheus":
    st.title("Monitoring : Grafana / Prometheus")
    st.markdown("""Trois dashboard on était mis en place et configurer
- Linux Exporter Dashboard 2025
- Windows Exporter Dashboard 2025
- FastAPI Observability
""")
    st.write("### FastAPI Observability")
    st.markdown("""Le dashboard FastAPI est dédié à la supervision des services applicatifs. Il affiche le nombre de requêtes reçues par endpoint, réparties par méthode et par période, ainsi que les temps de réponse moyens.
Le tableau de bord inclut également des panneaux de suivi du pourcentage de réponses réussies, des distributions de latence et d’autres métriques applicatives fournies par l’instrumentation Prometheus.
Chaque composant visuel met en avant une catégorie spécifique : volumétrie des requêtes, durée d'exécution, répartition des codes de statut et activité par endpoint, facilitant ainsi la surveillance opérationnelle de l’API.
""")
    st.write("### Linux Exporter et Windows Exporter Dashboard 2025")
    st.markdown("""Ces deux dashbords présente l’ensemble des métriques essentielles liées au fonctionnement du serveur. Il inclut des jauges de charge CPU, d’utilisation mémoire, d’usage du swap, d’occupation du système de fichiers, ainsi que des informations générales comme le nombre de cœurs, la mémoire totale et le temps de fonctionnement.
Des graphiques détaillés complètent ces indicateurs en affichant l’évolution de la charge CPU, de la mémoire, de l’utilisation disque et du trafic réseau sur différentes périodes.
L’interface propose également des sections regroupant les métriques avancées : mémoire, processus système, réseaux, I/O et autres informations bas niveau collectées par Node Exporter.
""")

# =====================================================
# 8. CI/CD SEBASTIEN
# =====================================================

elif page == "8. CI/CD : GitHub Actions":
    st.title("CI/CD : GitHub Actions")
    st.markdown("""
Le pipeline est divisé en deux flux distincts : 
* une chaîne d’intégration pour valider la qualité du code (`ci.yml`) 
* une chaîne de déploiement pour la mise en production (`cd.yml`)

## ✅ Intégration Continue (CI)

Le workflow CI est déclenché automatiquement à chaque `push` ou `pull request` sur la branche `master`.
Son objectif est de garantir la qualité du code Python avant toute fusion ou déploiement et l’exécution d’une couverture de tests pour garantir l’absence de régression.


### Étapes clés du pipeline d’exécution de la CI

* Environnement : Exécution sur une machine virtuelle Ubuntu avec Python 3.11.
* Gestion des dépendances : Utilisation de `uv` (un gestionnaire d’environnement virtuel et de paquets ultra-rapide).
* Qualité du code (Linting & Formatting) :
  > Le code est analysé et vérifié par `ruff` (remplaçant moderne d’outils comme Flake8 ou Black).

  > Le pipeline échoue si le code ne respecte pas les normes de formatage définies.

* Tests automatisés :
  > Lancement des tests unitaires via `pytest`.

  > Le script vérifie la présence de fichiers de test avant de lancer la commande pour éviter les erreurs inutiles.

  > Rapport de couverture : Upload automatique des rapports de couverture de code vers Codecov si les tests réussissent.



## 🚀 Déploiement Continu (CD)

Le workflow CD est orchestré pour se lancer uniquement après la réussite du workflow CI.
Il gère la construction des images Docker et leur déploiement sur un serveur distant (infrastructure Oracle Cloud).


### Étapes clés du pipeline d’exécution de la CD

* Construction des Images (Build & Push)

  > Ce job prépare les conteneurs pour la production. Pour optimiser l’espace disque, les services sont construits séquentiellement avec un nettoyage systématique entre chaque étape.[2]

  > Registre de conteneurs : Les images sont stockées sur le GitHub Container Registry (GHCR).


* Déploiement (Deploy SSH)

  > Une fois les images construites, le déploiement s’effectue via SSH sur le serveur cible.

  > Transfert de configuration : Copie des fichiers `docker-compose*.yml` vers le serveur via SCP.

  > Mise à jour des services
  > * Connexion au registre GHCR depuis le serveur.
  > * Téléchargement des nouvelles images (`docker compose pull`).
  > * Redémarrage des conteneurs en tâche de fond (`docker compose up -d`).
  > * Nettoyage des anciennes images inutilisées pour libérer de l’espace (`docker image prune`).


## 📌 Récapitulatif

| Composant               | Outils / Technologies               |
| ----------------------- | ----------------------------------- |
| Gestionnaire de paquets | `uv` (Performance)                  |
| Linter / Formatter      | `ruff`                              |
| Tests                   | `pytest` + Codecov                  |
| Conteneurisation        | Docker + Docker Buildx (Multi-arch) |
| Registre d’images       | GitHub Container Registry (ghcr.io) |
| Déploiement             | SSH + Docker Compose                |
""")

# =====================================================
# 9. CONCLUSION MARC
# =====================================================

elif page == "9. Conclusion & Opportunités futures":
    st.title("🏁 Conclusion & Opportunités futures")

    st.markdown("""
# 🎓 Conclusion du projet Rakuten – Classification Multimodale & MLOps

Ce projet nous a permis de couvrir **toute la chaîne de valeur d’un système de Machine Learning moderne**, 
depuis la donnée brute jusqu’au déploiement d’un modèle servable.  
Nous avons développé un modèle multimodal texte + image et appris à le déployer en suivant les principes structurés de l’ingénierie MLOps.

---

## ✅ Ce que nous avons accompli

### **1. Construire un modèle ML complet**
Nous avons appliqué l’ensemble des techniques apprises dans le cursus :
- NLP (cleaning, TF-IDF, traitement texte)
- Computer Vision (embeddings ResNet50)
- Classification XGBoost multimodale
- Optimisation, métriques, validation

### **2. Intégrer les bonnes pratiques MLOps**
Le projet a permis de mettre en œuvre :
- **Pipelines reproductibles** (cleaning → preprocessing → train)
- **Suivi d’expérience MLflow**
- **Versionnement des modèles**
- **API d’inférence** prête à l’emploi
- **Microservices Docker** interconnectés
- **Orchestration docker-compose**
- **Base de données MongoDB** comme source unique des données nettoyées

Ces outils peuvent paraître complexes, mais en progressant étape par étape, nous avons réussi à les maîtriser et à en faire un système stable et fonctionnel.

### **3. Un vrai travail d’équipe**
Le projet a été réalisé en équipe :
- **Chacun a apporté sa vision, ses compétences et son approche**
- Les décisions ont été **construites collectivement**
- Le fonctionnement en groupe a permis de **résoudre des problèmes techniques réels**, 
  notamment sur l'architecture globale, la gestion de Docker, les connexions API, les databases, les configurations MLflow, Airflow...

Ce travail collaboratif a joué un rôle essentiel dans l’avancement et la réussite du projet.

---

# 🚀 Opportunités futures

Même si notre système fonctionne en local et en docker, plusieurs axes d’amélioration s’ouvrent :

### **📌 1. Déploiement sur serveur cloud**
- hébergement API + Streamlit
- stockage MinIO en cloud
- modèle servable 24/7

### **📌 2. Optimisation de l’architecture**
- réduction du nombre de conteneurs
- rationalisation des services
- meilleure modularité pour la maintenance

### **📌 3. Optimisation des performances**
- accélération du preprocessing
- batching GPU pour XGBoost

### **📌 4. Amélioration de la qualité du code**
- refactoring du pipeline
- réduction du code redondant
- structuration plus modulaire

### **📌 5. Amélioration de l’UX / UI (frontend)**
- meilleure ergonomie Streamlit
- affichage image + texte dans les prédictions
- navigation simplifiée

### **📌 6. Robustesse & Qualité**
- tests unitaires (pytest)
- gestion d’erreurs API
- monitoring du drift (Evidently)
- alertes Prometheus / Grafana

---

# 🎯 Conclusion finale

Nous avons montré que **nous savons concevoir, entraîner, déployer et surveiller un modèle de Machine Learning complet**.  
Nous avons acquis **la culture Data / IA / MLOps** moderne et la capacité de gérer des environnements techniques complexes.

Le système fonctionne, le pipeline est cohérent, et surtout…

👉 **Nous savons maintenant créer ET déployer un modèle ML dans un environnement MLOps complet.**

Un projet riche, formateur, et qui ouvre naturellement la porte à des déploiements plus ambitieux.

""")

# =====================================================
#                 PAGE : DEMO PREDICTION
# =====================================================

elif page == "Démo : prédiction Rakuten":
    st.title("Démo : prédiction Rakuten")

    # ---------- LOGIN ----------
    st.header("Authentification")

    user = st.text_input("User", "user")
    password = st.text_input("Password", "rakuten_project", type="password")

    if st.button("Obtenir un jeton"):
        headers = {"Authorization": f"Bearer {user}:{password}"}
        resp = requests.post(f"{API_URL}/login", headers=headers)

        if resp.status_code == 200:
            st.session_state["token"] = resp.json()["token"]
            st.success("Jeton reçu")
        else:
            st.error(f"Erreur login : {resp.text}")

    # ---------- PREDICTION ----------
    st.header("Sélection d'un produit")

    if "token" in st.session_state:
        csv_path = os.path.join(RAW_DIR, "X_test_update.csv")
        df_full = pd.read_csv(
            csv_path
        )  # Charger un échantillon de 5 lignes une seule fois
        # Bouton pour recharger 5 lignes aléatoires
        if st.button("🔄 Recharger 5 produits au hasard"):
            st.session_state["rakuten_sample"] = df_full.sample(n=5).reset_index(
                drop=True
            )

        # Si pas encore d'échantillon, en générer un
        if "rakuten_sample" not in st.session_state:
            st.session_state["rakuten_sample"] = df_full.sample(n=5).reset_index(
                drop=True
            )

        df_sample = st.session_state["rakuten_sample"]

        st.markdown("Clique sur une ligne dans le tableau pour la sélectionner :")

        # Tableau cliquable
        event = st.dataframe(
            df_sample[["designation", "description"]],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        selected_row = None
        if hasattr(event, "selection") and event.selection and event.selection.rows:
            pos = event.selection.rows[0]  # position dans df_sample
            selected_row = df_sample.iloc[pos]

        if selected_row is not None:
            # Construction du chemin d'image
            image_filename = (
                "image_"
                + str(selected_row["imageid"])
                + "_product_"
                + str(selected_row["productid"])
                + ".jpg"
            )
            image_path = os.path.join(IMG_DIR, "image_test", image_filename)

            col1, col2 = st.columns(2)

            img = None
            with col1:
                st.subheader("Image du produit")
                if os.path.exists(image_path):
                    img = Image.open(image_path)
                    st.image(img, width=300)
                else:
                    st.write("Image introuvable.")

            with col2:
                st.subheader("Texte du produit")
                st.markdown("**Désignation :**")
                st.write(selected_row["designation"])
                st.markdown("**Description :**")
                st.write(selected_row["description"])

            if st.button("🚀 Lancer la prédiction sur ce produit"):
                if img is None:
                    st.error("Impossible de prédire : image introuvable.")
                else:
                    # encodage image en base64
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG")
                    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

                    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                    payload = {
                        "designation": str(selected_row["designation"] or ""),
                        "description": str(selected_row["description"] or ""),
                        "image_base64": img_b64,
                    }
                    resp = requests.post(
                        f"{API_URL}/predict", headers=headers, json=payload
                    )

                    if resp.status_code == 200:
                        data = resp.json()["data"]

                        st.subheader("Résultat de la prédiction")
                        st.markdown(f"**Catégorie prédite :** {data.get('category')}")
                        st.markdown(f"**Code prédit :** {data.get('predicted_code')}")
                    else:
                        st.error(f"Erreur predict : {resp.text}")
        else:
            st.info(
                "Sélectionne une ligne dans le tableau pour afficher l'image et lancer une prédiction."
            )
    else:
        st.info("Veuillez d'abord obtenir un jeton.")
