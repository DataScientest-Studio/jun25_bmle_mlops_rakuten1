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
## 🎯 Objectif du pipeline
Décrire les étapes complètes qui permettent de construire le modèle multimodal *texte + image*.

---

## 📦 Pipeline Machine Learning

### **1️⃣ Préprocessing texte**
- Nettoyage HTML (BeautifulSoup)
- Nettoyage accents, ponctuation, caractères spéciaux
- Fusion désignation + description
- TF-IDF 20 000 features (unigrammes & bigrammes)

### **2️⃣ Préprocessing image**
- Extraction embeddings **ResNet50 2048-D**
- Resize + normalisation ImageNet
- Gestion images manquantes
- Sauvegarde `.npy`

### **3️⃣ Fusion des features**
- Conversion embeddings → sparse CSR
- Concaténation TF-IDF + Image
- Matrice unique `X_all_sparse.npz`

### **4️⃣ Entraînement XGBoost**
- Objective : multi:softprob
- Split train/validation
- Callback tqdm
- Sauvegarde :
  - `xgb_fusion.json`
  - `label_encoder.joblib`
  - `metrics_fusion.json`

### **5️⃣ Évaluation**
- Accuracy
- F1 score pondéré
- Matrice de confusion normalisée

---

## 📊 Suivi MLflow
- Tracking paramètres
- Tracking métriques
- Stockage artefacts
- Versionnement des modèles
Base de données :
- MongoDB contenant produits + métadonnées
""")

    st.subheader("🔁 Schéma du pipeline (agrandi)")

    st.graphviz_chart("""
digraph {
    rankdir=LR;
    node [shape=box, style="rounded,filled", color="#3477eb", fontcolor=white, fontsize=18];

    A [label="CSV + Images\nDonnées brutes"];
    B [label="Nettoyage texte\nHTML + regex"];
    C [label="TF-IDF\n20k features"];
    D [label="ResNet50\nEmbeddings 2048-D"];
    E [label="Fusion sparse\nTF-IDF + Image"];
    F [label="XGBoost\nTraining"];
    G [label="Artefacts\nModèle + Encodeur + Metrics"];
    H [label="MLflow\nTracking"];

    A -> B -> C -> E;
    A -> D -> E;
    E -> F -> G;
    F -> H;
}
""", use_container_width=True)



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
