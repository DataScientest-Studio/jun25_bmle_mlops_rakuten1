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

Le pipeline est divisé en deux flux distincts : une chaîne d'intégration pour valider la qualité du code (ci.yml) et une chaîne de déploiement pour la mise en production (cd.yml).
1. Intégration Continue (CI)

Le workflow CI est déclenché automatiquement à chaque push ou pull request sur la branche master. Son objectif est de garantir la qualité du code Python avant toute fusion ou déploiement.
Étapes clés du pipeline :

    Environnement : Exécution sur une machine virtuelle Ubuntu avec Python 3.11.

Gestion des dépendances : Utilisation de uv (un gestionnaire de paquets ultra-rapide) pour créer l'environnement virtuel et installer les dépendances du projet.

Qualité du code (Linting & Formatting) :

    Le code est analysé et vérifié par ruff (remplaçant moderne de outils comme Flake8 ou Black).

    Le pipeline échoue si le code ne respecte pas les normes de formatage définies.

Tests automatisés :

    Lancement des tests unitaires via pytest.

    Le script vérifie intelligemment la présence de fichiers de test avant de lancer la commande pour éviter les erreurs inutiles.

Rapport de couverture : Upload automatique des rapports de couverture de code vers Codecov si les tests réussissent.


2. Déploiement Continu (CD)

Le workflow CD est orchestré pour se lancer uniquement après la réussite du workflow CI. Il gère la construction des images Docker et leur déploiement sur un serveur distant (infrastructure Oracle Cloud).
Construction des Images (Build & Push)

Ce job prépare les conteneurs pour la production. Pour optimiser l'espace disque, les services sont construits séquentiellement avec un nettoyage systématique entre chaque étape.


    Registre de conteneurs : Les images sont stockées sur le GitHub Container Registry (GHCR).

    Services construits :

        Le pipeline construit et pousse actuellement les images pour : API (FastAPI), Airflow, MLflow, MongoDB, et Prometheus.


Note importante : Les services Streamlit (Frontend), Trainer, et Predictor sont actuellement commentés dans le fichier cd.yml et ne sont donc pas construits automatiquement pour le moment.

Déploiement (Deploy SSH)

Une fois les images construites, le déploiement s'effectue via SSH sur le serveur cible.

    Transfert de configuration : Copie des fichiers docker-compose*.yml vers le serveur via SCP.

Mise à jour des services :

    Connexion au registre GHCR depuis le serveur.

    Téléchargement des nouvelles images (docker compose pull).

    Redémarrage des conteneurs en tâche de fond (docker compose up -d).

    Nettoyage des anciennes images inutilisées pour libérer de l'espace (docker image prune).

| Composant               | Outils / Technologies               |
| ----------------------- | ----------------------------------- |
| Gestionnaire de paquets | uv (Performance)                    |
| Linter / Formatter      | ruff                                |
| Tests                   | pytest + Codecov                    |
| Conteneurisation        | Docker + Docker Buildx (Multi-arch) |
| Registre d'images       | GitHub Container Registry (ghcr.io) |
| Déploiement             | SSH + Docker Compose                |

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
