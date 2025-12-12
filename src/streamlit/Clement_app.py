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
    ],
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
    st.write("### Grestion de l'entrainement")
    st.markdown("""Le service d’entraînement propose un endpoint : /train.
Fonctionnement général
Après authentification :
L’API appelle le module d’entraînement du modèle.
Le modèle est réentraîné selon les procédures définies dans ce module externe.
L’API retourne un message indiquant que l’authentification est correcte, que l’entraînement s’est bein effectué et que les données retournées par le processus d’entraînement.
En cas d’erreur ou d’absence de token valide, une erreur est renvoyée.
""")
    st.write("### Grestion de la prediction")
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
    st.write("### Grestion de la vérification et du monitoring")
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
