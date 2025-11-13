"""
=====================================================================
🏋️‍♂️  Script : train.py — Entraînement du modèle Rakuten XGBoost fusion
=====================================================================

🎯 Objectif :
-------------
Ce script entraîne un modèle de classification multimodale (texte + image)
pour prédire le code produit Rakuten (`prdtypecode`) à partir de données
pré-fusionnées (features texte TF-IDF + features image ResNet).

Il assure :
  - le chargement des jeux de données déjà pré-traités (.npz, .npy),
  - l’encodage des labels,
  - l’entraînement du modèle XGBoost avec suivi des métriques via MLflow,
  - la sauvegarde des artefacts (modèle, encodeur, métriques).

📁 Données attendues :
----------------------
Les fichiers doivent être présents dans :  data/processed/
  - X_train.npz   : features d’entraînement (texte + image)
  - X_val.npz     : features de validation
  - y_train.npy   : labels d’entraînement
  - y_val.npy     : labels de validation

🧠 Sorties générées :
---------------------
Les artefacts du modèle sont sauvegardés dans :  data/models/
  - xgb_fusion.json          → modèle XGBoost entraîné
  - label_encoder.joblib     → encodeur des labels scikit-learn
  - metrics_fusion.json      → métriques (accuracy, F1)

📊 Suivi des expériences :
--------------------------
Les logs d’expériences sont enregistrés dans :  mlruns/
  - tracking local MLflow (backend = file:./mlruns)
  - enregistre les paramètres, métriques et artefacts

🔁 Fonction principale :
------------------------
train() :
    • charge les données
    • entraîne le modèle
    • log les métriques et artefacts MLflow
    • retourne un dictionnaire Python :
        {"status": "done", "accuracy": float, "f1": float}

📦 Utilisation :
----------------
▶️ En ligne de commande :
    python src/train/train.py

▶️ En module (API, orchestrateur, etc.) :
    from train.train import train
    result = train()

⚙️ Intégration Docker :
-----------------------
Le Dockerfile associé exécute ce script via :
    CMD ["python", "-m", "train.train"]
avec volumes montés pour `data/` et `mlruns/`.

=====================================================================
"""

# --- train.py : Entraînement XGBoost fusion texte+image avec MLflow ---
import json
import os
from datetime import datetime

import joblib
import mlflow
import mlflow.xgboost
import numpy as np
import xgboost as xgb
from scipy import sparse
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.preprocessing import LabelEncoder
from tqdm.auto import tqdm

from src.data.clean_data import calcul_lignes_a_lire, clean_data
from src.data.preprocess_data import preprocess_data


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

# 🔹 MLflow local : stocke les runs dans le dossier mlruns à la racine
mlflow.set_tracking_uri(f"file:{MLRUNS_DIR}")
mlflow.set_experiment("rakuten_xgb_fusion")


def train():
    print("🧹 Starting data cleaning process...")
    nb_lignes = calcul_lignes_a_lire(datetime.now().strftime("%Y-%m-%d"))
    clean_data(input_dir=RAW_DIR, images_dir=IMG_DIR, nbre_lignes=nb_lignes)

    print("⚙️ Starting data preprocessing...")
    preprocess_data(
        output_dir=DATA_DIR, input_model=os.path.join(MODEL_DIR, "resnet50-weights.pth")
    )

    print("🚀 Starting training process...")

    # === 1️⃣ Chargement des données pré-fusionnées ===
    X_train = sparse.load_npz(os.path.join(DATA_DIR, "X_train.npz"))
    X_val = sparse.load_npz(os.path.join(DATA_DIR, "X_val.npz"))
    y_train = np.load(os.path.join(DATA_DIR, "y_train.npy"))
    y_val = np.load(os.path.join(DATA_DIR, "y_val.npy"))

    print(f"📦 X_train: {X_train.shape}, X_val: {X_val.shape}")
    print(f"📊 y_train: {y_train.shape}, y_val: {y_val.shape}")

    # === 2️⃣ Encodage des labels ===
    encoder = LabelEncoder()
    y_train_enc = encoder.fit_transform(y_train)
    y_val_enc = encoder.transform(y_val)

    dtrain = xgb.DMatrix(X_train, label=y_train_enc)
    dval = xgb.DMatrix(X_val, label=y_val_enc)

    # === 3️⃣ Paramètres du modèle ===
    device = "cuda" if gpu_available() else "cpu"
    params = {
        "objective": "multi:softprob",
        "num_class": len(np.unique(y_train_enc)),
        "eval_metric": ["mlogloss", "merror"],
        "eta": 0.1,
        "max_depth": 8,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "tree_method": "hist",
        "device": device,
    }

    num_round = 50
    evals_result = {}

    # === 4️⃣ Callback de progression ===
    class TQDMProgress(xgb.callback.TrainingCallback):
        def __init__(self, total):
            self.pbar = tqdm(total=total, desc="🧠 Training")

        def after_iteration(self, model, epoch, evals_log):
            self.pbar.update(1)
            tr = evals_log["train"]["mlogloss"][-1]
            va = evals_log["val"]["mlogloss"][-1]
            self.pbar.set_postfix({"train": f"{tr:.4f}", "val": f"{va:.4f}"})
            return False

        def after_training(self, model):
            self.pbar.close()
            return model

    # === 5️⃣ Entraînement + suivi MLflow ===
    with mlflow.start_run(run_name="train_xgb_fusion"):
        mlflow.log_params(params)

        bst = xgb.train(
            params=params,
            dtrain=dtrain,
            num_boost_round=num_round,
            evals=[(dtrain, "train"), (dval, "val")],
            evals_result=evals_result,
            verbose_eval=False,
            callbacks=[TQDMProgress(num_round)],
        )

        # === 6️⃣ Évaluation sur validation ===
        y_pred = np.argmax(bst.predict(dval), axis=1)
        acc = accuracy_score(y_val_enc, y_pred)
        f1 = f1_score(y_val_enc, y_pred, average="weighted")

        print(f"✅ Accuracy: {acc:.4f} | F1: {f1:.4f}")
        print("=== Rapport (résumé) ===")
        print(classification_report(y_val_enc, y_pred, digits=3)[:800])

        mlflow.log_metrics({"accuracy": float(acc), "f1": float(f1)})

        # === 7️⃣ Sauvegardes locales ===
        model_path = os.path.join(MODEL_DIR, "xgb_fusion.json")
        encoder_path = os.path.join(MODEL_DIR, "label_encoder.joblib")
        metrics_path = os.path.join(MODEL_DIR, "metrics_fusion.json")

        bst.save_model(model_path)
        joblib.dump(encoder, encoder_path)
        json.dump({"accuracy": float(acc), "f1": float(f1)}, open(metrics_path, "w"))

        # === 8️⃣ Logging MLflow des artefacts ===
        mlflow.xgboost.log_model(bst, artifact_path="xgb_model")
        mlflow.log_artifact(encoder_path, artifact_path="preprocessing")
        mlflow.log_artifact(metrics_path, artifact_path="metrics")

    print("💾 Model saved:", model_path)
    print("✅ Training done successfully.")
    return {"status": "done", "accuracy": acc, "f1": f1}


def gpu_available():
    """
    Teste si un GPU compatible CUDA est disponible pour XGBoost.

    Essaie d'entraîner un modèle minimal avec les paramètres GPU.
    Si l'entraînement réussit, retourne True (GPU disponible),
    sinon retourne False (pas de GPU ou erreur de configuration).

    Utile pour adapter dynamiquement le paramètre 'device' lors de l'entraînement
    afin d'utiliser le GPU si possible, sinon CPU.
    """
    try:
        params = {"tree_method": "hist", "device": "cuda"}
        dtrain = xgb.DMatrix(np.array([[0, 1], [1, 0]]), label=np.array([0, 1]))
        xgb.train(params=params, dtrain=dtrain, num_boost_round=1)
        print("🔥 GPU disponible - entraînement accéléré activé")
        return True
    except xgb.core.XGBoostError:
        print("🐌 GPU non disponible - utilisation du CPU")
        return False


# --- Point d'entrée pour Docker ou CLI ---
if __name__ == "__main__":
    result = train()
    print(json.dumps(result, indent=2))
