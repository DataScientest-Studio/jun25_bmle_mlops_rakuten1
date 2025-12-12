import streamlit as st
import requests

API_URL = "http://rakuten_predictor:8080"

st.set_page_config(layout="wide")

# =====================================================
#               SIDEBAR : MENU
# =====================================================

st.sidebar.title("Navigation du projet")

page = st.sidebar.radio(
    "Aller à :",
    [
        "Démo : prédiction Rakuten",
        "1. Intro : contexte & objectifs",
        "2. Architecture globale / Dockerisation / Environnement développement",
        "3. Pipelines : train & predict + DB",
        "4. API",
        "5. Model Tracking : MLflow",
        "6. Automatisation : Airflow - drift / Evidently",
        "7. Monitoring : Grafana / Prometheus",
        "8. CI/CD : GitHub Actions",
        "9. Conclusion & Opportunités futures",
    ]
)

# =====================================================
#                 PAGE : DEMO PREDICTION
# =====================================================

if page == "Démo : prédiction Rakuten":

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
    st.header("Prédiction d'un produit aléatoire")

    if "token" in st.session_state:
        if st.button("Prédire un produit"):
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            resp = requests.post(f"{API_URL}/predict", headers=headers)

            if resp.status_code == 200:
                data = resp.json()["data"]

                st.subheader("Catégorie prédite")
                st.write(data.get("category"))

                st.subheader("Code prédict")
                st.write(data.get("predicted_code"))

                st.subheader("Désignation")
                st.write(data.get("designation"))

                st.subheader("Description")
                st.write(data.get("description"))
            else:
                st.error(f"Erreur predict : {resp.text}")

    else:
        st.info("Veuillez d'abord obtenir un jeton.")

# =====================================================
# 1. INTRO MARC
# =====================================================


elif page == "1. Intro : contexte & objectifs":

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

elif page == "2. Architecture globale / Dockerisation / Environnement développement":
    st.title("Architecture globale / Dockerisation / Environnement développement")
    st.markdown("""
Architecture globale du projet :
- FastAPI pour la prédiction
- Streamlit pour l'interface utilisateur
- MongoDB pour stocker les données brutes
- Jobs de preprocessing et entraînement
- MLflow pour le suivi des modèles
- Airflow pour l'automatisation
- Monitoring système + API

Environnement :
- Développement via containers Docker
- Réseau interne Docker Compose
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

    st.graphviz_chart("""
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
""", width="stretch")



# =====================================================
# 4. API CLEMENT
# =====================================================

elif page == "4. API":
    st.title("API")
    st.markdown("""
FastAPI expose :
- Endpoint /login
- Endpoint /predict
- Gestion du token
- Validation des entrées
""")

# =====================================================
# 5. MLflow PASCAL
# =====================================================

elif page == "5. Model Tracking : MLflow":
    st.title("Model Tracking : MLflow")
    st.markdown("""
MLflow utilisé pour :
- Tracking des runs
- Paramètres / hyperparamètres
- Métriques
- Artefacts (modèles, encoders)
""")

# =====================================================
# 6. AIRFLOW + DRIFT
# =====================================================

elif page == "6. Automatisation : Airflow - drift / Evidently":
    st.title("Automatisation : Airflow - drift / Evidently")
    st.markdown("""
Airflow orchestre :
- Préprocessing
- Fusion
- Entraînement automatique
- Publication du modèle

Evidently pour :
- Détection de dérive
- Monitoring statistique
""")

# =====================================================
# 7. MONITORING PASCAL CLEMENT
# =====================================================

elif page == "7. Monitoring : Grafana / Prometheus":
    st.title("Monitoring : Grafana / Prometheus")
    st.markdown("""
Prometheus :
- Scraping métriques FastAPI
- CPU, RAM, latence

Grafana :
- Dashboards
- Visualisation des métriques
""")

# =====================================================
# 8. CI/CD SEBASTIEN
# =====================================================

elif page == "8. CI/CD : GitHub Actions":
    st.title("CI/CD : GitHub Actions")
    st.markdown("""
GitHub Actions :
- Tests unitaires
- Build & Push Docker
- Déploiement automatique
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
