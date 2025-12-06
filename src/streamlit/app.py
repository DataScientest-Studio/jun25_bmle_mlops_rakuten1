import streamlit as st
import requests

API_URL = "http://rakuten_predictor:8080"

# ==========================
#       SIDEBAR MENU
# ==========================
st.sidebar.title("📚 Agenda du projet")
page = st.sidebar.selectbox(
    "Navigation",
    [
        "Prediction Rakuten",
        "Pipeline",
        "Architecture globale",
        "MLOps : Dockerisation",
        "MLOps : MLflow",
        "MLOps : Airflow",
        "MLOps : Grafana / Prometheus",
        "MLOps : GitHub Actions",
        "MLOps : Opportunités & améliororations futures",
    ]
)

# ==========================
#     PAGE : PREDICTION
# ==========================
if page == "Prediction Rakuten":

    st.title("🔮 Prédiction Rakuten – Interface Streamlit")

    # ---------- LOGIN ----------
    st.header("🔐 Authentification")

    user = st.text_input("User", "user")
    password = st.text_input("Password", "rakuten_project", type="password")

    if st.button("Obtenir un jeton"):
        headers = {"Authorization": f"Bearer {user}:{password}"}
        resp = requests.post(f"{API_URL}/login", headers=headers)

        if resp.status_code == 200:
            token = resp.json()["token"]
            st.session_state["token"] = token
            st.success("Jeton reçu !")
            st.code(token)
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

                st.success("Prédiction réussie !")

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


# ==========================
#       AUTRES PAGES
# ==========================

elif page == "Pipeline":
    st.title("🛠️ Pipeline du projet Rakuten")
    st.info("Contenu à compléter…")

elif page == "Architecture globale":
    st.title("🏗️ Architecture globale du projet")
    st.info("Contenu à compléter…")

elif page == "MLOps : Dockerisation":
    st.title("🐳 MLOps – Dockerisation & Conteneurisation")
    st.info("Contenu à compléter…")

elif page == "MLOps : MLflow":
    st.title("📊 MLOps – Tracking MLflow")
    st.info("Contenu à compléter…")

elif page == "MLOps : Airflow":
    st.title("🪂 MLOps – Airflow & Orchestration")
    st.info("Contenu à compléter…")

elif page == "MLOps : Grafana / Prometheus":
    st.title("📈 Monitoring – Grafana & Prometheus")
    st.info("Contenu à compléter…")

elif page == "MLOps : GitHub Actions":
    st.title("🤖 CI/CD – GitHub Actions")
    st.info("Contenu à compléter…")

elif page == "MLOps : Opportunités & améliororations futures":
    st.title("🚀 Opportunités & Améliorations futures")
    st.info("Contenu à compléter…")
