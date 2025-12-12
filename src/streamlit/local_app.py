import streamlit as st
import requests

API_URL = "http://rakuten_predictor:8080"

st.set_page_config(layout="wide")

# =====================================================
#               SIDEBAR : MENU PROPRE
# =====================================================

st.sidebar.title("📚 Navigation du projet")

page = st.sidebar.radio(
    "Aller à :",
    [
        "📌 Prediction Rakuten",
        "📌 Pipeline",
        "📌 Architecture globale",
        "📌 MLOps : Dockerisation",
        "📌 MLOps : MLflow",
        "📌 MLOps : Airflow",
        "📌 MLOps : Grafana / Prometheus",
        "📌 MLOps : GitHub Actions",
        "📌 MLOps : Opportunités futures"
    ]
)


# =====================================================
#                 PAGE : PREDICTION
# =====================================================

if page == "📌 Prediction Rakuten":

    st.title("🔮 Prédiction Rakuten – Interface Streamlit")

    # ---------- LOGIN ----------
    st.header("🔐 Authentification")

    user = st.text_input("User", "user")
    password = st.text_input("Password", "rakuten_project", type="password")

    if st.button("Obtenir un jeton"):
        headers = {"Authorization": f"Bearer {user}:{password}"}
        resp = requests.post(f"{API_URL}/login", headers=headers)

        if resp.status_code == 200:
            st.session_state["token"] = resp.json()["token"]
            st.success("Jeton reçu !")
        else:
            st.error(f"Erreur login : {resp.text}")

    # ---------- PREDICTION ----------
    st.header("🔮 Prédiction d'un produit aléatoire")

    if "token" in st.session_state:
        if st.button("Prédire un produit"):
            headers = {"Authorization": f"Bearer {st.session_state['token']}"}
            resp = requests.post(f"{API_URL}/predict", headers=headers)

            if resp.status_code == 200:
                data = resp.json()["data"]

                st.write("### 🏷️ Catégorie prédite")
                st.write(data.get("category"))

                st.write("### 🔢 Code prédict")
                st.write(data.get("predicted_code"))

                st.write("### ✍️ Désignation")
                st.write(data.get("designation"))

                st.write("### 📄 Description")
                st.write(data.get("description"))
            else:
                st.error(f"Erreur predict : {resp.text}")

    else:
        st.info("Veuillez d'abord obtenir un jeton.")



# =====================================================
#                    PAGE : PIPELINE
# =====================================================

elif page == "📌 Pipeline":

    st.title("🛠️ Pipeline du projet Rakuten")

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
#                   AUTRES PAGES
# =====================================================

elif page == "📌 Architecture globale":
    st.title("🏗️ Architecture globale")
    st.markdown("""
## 🧩 Composants
- FastAPI : prédiction + authentification
- Streamlit : UI
- MongoDB : données brutes
- Preprocessing : texte & image
- Modèle XGBoost fusion
- MLflow : suivi des expériences
""")

elif page == "📌 MLOps : Dockerisation":
    st.title("🐳 Dockerisation")
    st.markdown("""
## 🐳 Conteneurisation
- Chaque service = 1 image Docker
- Réseau interne `mlops-network`
- Orchestration via docker-compose
""")

elif page == "📌 MLOps : MLflow":
    st.title("📊 MLflow")
    st.markdown("""
- Tracking des runs
- Hyperparamètres
- Métriques
- Artefacts (modèle + encoder)
""")

elif page == "📌 MLOps : Airflow":
    st.title("🪂 Airflow")
    st.markdown("""
- Pipeline d'entraînement automatique
- DAG : preprocessing → fusion → train → publish
""")

elif page == "📌 MLOps : Grafana / Prometheus":
    st.title("📈 Monitoring")
    st.markdown("""
- Monitoring CPU / RAM / latence API
- Tableaux de bord sur Grafana
""")

elif page == "📌 MLOps : GitHub Actions":
    st.title("🤖 CI/CD")
    st.markdown("""
- Tests automatiques
- Build Docker
- Push automatique en registry
""")

elif page == "📌 MLOps : Opportunités futures":
    st.title("🚀 Opportunités futures")
    st.markdown("""
- Passage à BERT / DistilBERT
- Fine-tuning CNN moderne (EfficientNet)
- Monitoring de dérive
- AutoML pour optimiser XGBoost
""")
