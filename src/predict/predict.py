# src/api/predict.py
import argparse
import base64
import io
import json
import os
from typing import Dict, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
import torch
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
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MLRUNS_DIR = os.path.join(BASE_DIR, "mlruns")

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(MLRUNS_DIR, exist_ok=True)

print("📂 BASE_DIR :", BASE_DIR)
print("📂 RAW_DIR :", RAW_DIR)
print("📂 IMG_DIR :", IMG_DIR)
print("📂 DATA_DIR :", DATA_DIR)
print("📂 MODEL_DIR :", MODEL_DIR)
print("📂 MLRUNS_DIR :", MLRUNS_DIR)

# ---------- Config ----------
# MODEL_DIR = os.getenv("MODEL_DIR", "models")
# VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib"))
# MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(MODEL_DIR, "xgb_fusion.json"))
# ENCODER_PATH = os.getenv("ENCODER_PATH", os.path.join(MODEL_DIR, "label_encoder.joblib"))


def predict(designation: str, description: str, image: Image) -> dict:
    print("📦 Chargement des artefacts...")
    bst = xgb.Booster()
    bst.load_model(os.path.join(MODEL_DIR, "xgb_fusion.json"))
    encoder = joblib.load(os.path.join(MODEL_DIR, "label_encoder.joblib"))

    print("🧹 Data cleaning...")
    data_cleaned = clean_one_row(designation, description, image)
    #    print(data_cleaned)
    df_clean = pd.DataFrame([data_cleaned])
    df_clean["text"] = df_clean["designation"].fillna("") + " " + df_clean["description"].fillna("")

    preprocessor = Preprocessor()
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
    result = predict(row["designation"].values[0], row["description"].values[0], img)

    print("Retour predict : ", result)


if __name__ == "__main__":
    main()
