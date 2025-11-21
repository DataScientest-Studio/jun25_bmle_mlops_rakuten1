# src/api/predict.py
import argparse
import base64
import io
import json
import os
from typing import Dict, Optional, Tuple
import tempfile
import joblib
import numpy as np
import pandas as pd
import torch
import mlflow
import xgboost as xgb
from PIL import Image
from scipy.sparse import csr_matrix, hstack
from torchvision import models, transforms

from src.data.clean_data import clean_one_row
from src.data.preprocess_data import Preprocessor

# === Dictionnaire des catégories ===
cat_map = {
    10: "Livres et ouvrages culturels",
    40: "Jeux vidéo et accessoires",
    50: "Accessoires gaming",
    60: "Consoles rétro",
    1140: "Figurines Pop & licences geek",
    1160: "Cartes à collectionner",
    1180: "Jeux de figurines & wargames",
    1280: "Jouets enfants & bébés",
    1281: "Jeux et loisirs enfants",
    1300: "Drones et modèles réduits",
    1301: "Chaussettes & accessoires enfants",
    1302: "Jouets divers & loisirs créatifs",
    1320: "Puériculture & équipement bébé",
    1560: "Mobilier & articles de maison",
    1920: "Linge de maison & décoration textile",
    1940: "Alimentation & boissons",
    2060: "Décoration & accessoires saisonniers",
    2220: "Accessoires pour animaux",
    2280: "Magazines & journaux anciens",
    2403: "Livres, mangas & partitions",
    2462: "Lots jeux vidéo et consoles",
    2522: "Fournitures de papeterie",
    2582: "Mobilier et accessoires de jardin",
    2583: "Accessoires pour piscines et spas",
    2585: "Outils et équipements de jardinage",
    2705: "Essais & livres d’histoire",
    2905: "Jeux PC à télécharger & éditions spéciales",
}

# === 0️⃣ Gestion des chemins ===
# Récupère la racine du projet, peu importe d'où on exécute le script
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
IMG_DIR = os.path.join(RAW_DIR, "images", "images")

print("📂 BASE_DIR :", BASE_DIR)
print("📂 RAW_DIR :", RAW_DIR)
print("📂 IMG_DIR :", IMG_DIR)


def predict(designation: str, description: str, image: Image) -> dict:
    print("📦 Chargement des artefacts...")
    print("🛠️ Starting MLFlow configuration...")

    mlflow_host = os.getenv("MLFLOW_HOST", "localhost")
    mlflow.set_tracking_uri("http://" + mlflow_host + ":5000")

    client = mlflow.tracking.MlflowClient()

    experiment_name = "rakuten_xgb_fusion"
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        raise ValueError(f"L'expérience '{experiment_name}' n'existe pas.")

    runs = client.search_runs(
        experiment_ids=[experiment.experiment_id], order_by=["metrics.accuracy DESC"], max_results=1
    )

    if len(runs) == 0:
        raise ValueError("Aucun run trouvé dans MLflow pour cette expérience.")

    best_run = runs[0]
    best_run_id = best_run.info.run_id
    best_acc = best_run.data.metrics["accuracy"]

    print("📌 Best run ID :", best_run_id)
    print("📈 Best accuracy :", best_acc)

    model_uri = f"runs:/{best_run_id}/xgb_model"
    print("📥Chargement de XGBoost...")
    bst = mlflow.xgboost.load_model(model_uri)
    with tempfile.TemporaryDirectory() as tmpdir:
        # modèles
        print("📥Chargement du label encoder...")
        encoder_path = mlflow.artifacts.download_artifacts(
            f"runs:/{best_run_id}/Encoder/label_encoder.joblib", dst_path=tmpdir
        )
        encoder = joblib.load(encoder_path)
        print("📥Chargement du TFIDF...")
        tfidf_path = mlflow.artifacts.download_artifacts(
            f"runs:/{best_run_id}/TFIDF/tfidf_vectorizer.joblib", dst_path=tmpdir
        )
        tfidf = joblib.load(tfidf_path)

    print("🧹 Data cleaning...")
    data_cleaned = clean_one_row(designation, description, image)
    #    print(data_cleaned)
    df_clean = pd.DataFrame([data_cleaned])
    df_clean["text"] = df_clean["designation"].fillna("") + " " + df_clean["description"].fillna("")

    preprocessor = Preprocessor(tfidf=tfidf)
    X_tfidf, X_img = preprocessor.preprocess_data(df_clean)
    X = hstack([X_tfidf, X_img])

    dtest = xgb.DMatrix(X)

    # Prédiction
    proba = bst.predict(dtest)[0]
    pred_id = np.argmax(proba)
    prdtypecode = encoder.inverse_transform([pred_id])[0]

    category = cat_map.get(int(prdtypecode), "Non défini")
    print(f"\n🎯 Code produit prédit : {prdtypecode}")
    print(f"🪄 Catégorie : {category}\n")

    return {
        "predicted_code": int(prdtypecode),
        "category": category,
    }


# ---------- CLI ----------
def main():
    import time

    X_test = pd.read_csv(os.path.join(RAW_DIR, "X_test_update.csv"))
    row = X_test.sample(n=1)
    print(row)
    image_filename = (
        "image_"
        + str(row["imageid"].values[0])
        + "_product_"
        + str(row["productid"].values[0])
        + ".jpg"
    )
    image_path = os.path.join(IMG_DIR, "image_test", image_filename)
    print(image_path)
    if os.path.exists(image_path):
        img = Image.open(image_path)
    img.show()
    start = time.time()
    result = predict(row["designation"].values[0], row["description"].values[0], img)

    print("Retour predict : ", result)

    end = time.time()
    print(f"Temps d'exécution : {end - start} secondes")


if __name__ == "__main__":
    main()
