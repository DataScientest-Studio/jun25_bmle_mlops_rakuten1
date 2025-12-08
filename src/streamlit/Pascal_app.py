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
    st.title("Intro : contexte & objectifs")
    st.markdown("""
Présentation du projet Rakuten :
- Classification de produits à partir du texte et de l'image  
- Objectif : pipeline MLOps complet  
- Enjeux : industrialisation, reproductibilité, monitoring, automatisation
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
    st.title("Pipelines : train & predict + DB")

    st.markdown("""
Pipeline Training :
- Préprocessing texte (clean, TF-IDF)
- Embeddings d'image (ResNet50)
- Fusion texte + image
- Entraînement XGBoost
- Logging MLflow

Pipeline Prediction :
- Récupération produit aléatoire
- Même preprocessing
- Chargement modèle
- Retour catégorie prédite

Base de données :
- MongoDB contenant produits + métadonnées
""")

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
    st.title("Conclusion & Opportunités futures")
    st.markdown("""
- Industrialisation complète du pipeline ML
- Suivi et gouvernance des modèles
- Automatisation MLOps avancée

Futures évolutions :
- Passage modèles transformers
- Monitoring de dérive en continu
- Optimisation modèles + AutoML
""")
