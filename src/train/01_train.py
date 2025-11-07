# --- train.py : Entraînement XGBoost fusion texte+image avec MLflow ---
import os, json, joblib
import numpy as np
import xgboost as xgb
from scipy import sparse
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.preprocessing import LabelEncoder
from tqdm.auto import tqdm
import mlflow, mlflow.xgboost

# 🔹 MLflow local : stocke les runs dans le dossier ../mlruns
mlflow.set_tracking_uri("file:../mlruns")
mlflow.set_experiment("rakuten_xgb_fusion")

def train():
    print("🚀 Starting training process...")

    # === 1️⃣ Chargement des données pré-fusionnées ===
    X_train = sparse.load_npz("../data/processed/X_train_all_sparse.npz")
    X_val   = sparse.load_npz("../data/processed/X_val_all_sparse.npz")
    y_train = np.load("../data/processed/y_train.npy")
    y_val   = np.load("../data/processed/y_val.npy")

    print(f"📦 X_train: {X_train.shape}, X_val: {X_val.shape}")
    print(f"📊 y_train: {y_train.shape}, y_val: {y_val.shape}")

    # === 2️⃣ Encodage des labels ===
    encoder = LabelEncoder()
    y_train_enc = encoder.fit_transform(y_train)
    y_val_enc   = encoder.transform(y_val)

    dtrain = xgb.DMatrix(X_train, label=y_train_enc)
    dval   = xgb.DMatrix(X_val,   label=y_val_enc)

    # === 3️⃣ Paramètres du modèle ===
    params = {
        "objective": "multi:softprob",
        "num_class": len(np.unique(y_train_enc)),
        "eval_metric": ["mlogloss", "merror"],
        "eta": 0.1,
        "max_depth": 8,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "tree_method": "hist",
    }

    num_round = 200
    evals_result = {}

    os.makedirs("../data/models", exist_ok=True)

    # === 4️⃣ Callback de progression ===
    class TQDMProgress(xgb.callback.TrainingCallback):
        def __init__(self, total): self.pbar = tqdm(total=total, desc="🧠 Training")
        def after_iteration(self, model, epoch, evals_log):
            self.pbar.update(1)
            tr = evals_log["train"]["mlogloss"][-1]; va = evals_log["val"]["mlogloss"][-1]
            self.pbar.set_postfix({"train": f"{tr:.4f}", "val": f"{va:.4f}"})
            return False
        def after_training(self, model): self.pbar.close(); return model

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
        f1  = f1_score(y_val_enc, y_pred, average="weighted")

        print(f"✅ Accuracy: {acc:.4f} | F1: {f1:.4f}")
        print("=== Rapport (résumé) ===")
        print(classification_report(y_val_enc, y_pred, digits=3)[:800])

        mlflow.log_metrics({"accuracy": float(acc), "f1": float(f1)})

        # === 7️⃣ Sauvegardes locales ===
        model_path   = "../data/models/xgb_fusion.json"
        encoder_path = "../data/models/label_encoder.joblib"
        metrics_path = "../data/models/metrics_fusion.json"

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


# --- Point d'entrée pour Docker ou CLI ---
if __name__ == "__main__":
    result = train()
    print(json.dumps(result, indent=2))
