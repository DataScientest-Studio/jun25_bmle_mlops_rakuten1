# src/api/predict.py
import os, io, json, base64, argparse
from typing import Dict, Tuple, Optional

import numpy as np
from PIL import Image

import torch
from torchvision import models, transforms

from scipy.sparse import hstack, csr_matrix
import joblib
import xgboost as xgb


# ---------- Config ----------
MODEL_DIR = os.getenv("MODEL_DIR", "models")
VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib"))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(MODEL_DIR, "xgb_fusion.json"))
ENCODER_PATH = os.getenv("ENCODER_PATH", os.path.join(MODEL_DIR, "label_encoder.joblib"))

# ---------- Load artifacts ----------
def load_artifacts():
    if not os.path.exists(VECTORIZER_PATH):
        raise FileNotFoundError(f"TF-IDF vectorizer not found at {VECTORIZER_PATH}")
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"XGBoost model not found at {MODEL_PATH}")
    if not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError(f"LabelEncoder not found at {ENCODER_PATH}")

    vectorizer = joblib.load(VECTORIZER_PATH)
    encoder = joblib.load(ENCODER_PATH)

    booster = xgb.XGBClassifier()
    booster.load_model(MODEL_PATH)

    return vectorizer, encoder, booster


# ---------- Image embedding (ResNet50, avgpool) ----------
_resnet = None
_preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    # ImageNet normalization
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

def _get_resnet() -> torch.nn.Module:
    global _resnet
    if _resnet is None:
        m = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
        m.fc = torch.nn.Identity()  # take features before FC
        m.eval()
        _resnet = m
    return _resnet

def _load_image_from_input(image_path: Optional[str], image_b64: Optional[str]) -> Image.Image:
    if image_path:
        return Image.open(image_path).convert("RGB")
    if image_b64:
        # allow data URL or raw base64
        if image_b64.startswith("data:"):
            image_b64 = image_b64.split(",", 1)[1]
        buf = base64.b64decode(image_b64)
        return Image.open(io.BytesIO(buf)).convert("RGB")
    raise ValueError("Provide either --image PATH or --image_base64 STRING")

def extract_image_features(img: Image.Image) -> np.ndarray:
    with torch.no_grad():
        tensor = _preprocess(img).unsqueeze(0)  # (1,3,224,224)
        feats = _get_resnet()(tensor).numpy()   # (1, 2048)
    return feats.squeeze(0)  # (2048,)

# ---------- Text features ----------
def extract_text_features(vectorizer, text: str) -> csr_matrix:
    return vectorizer.transform([text])  # sparse (1, vocab)

# ---------- Fusion ----------
def fuse_features(text_sparse: csr_matrix, img_vec: np.ndarray) -> csr_matrix:
    # img_vec -> sparse row
    img_sparse = csr_matrix(img_vec.reshape(1, -1))
    return hstack([text_sparse, img_sparse], format="csr")

# ---------- Predict ----------
def predict_one(text: str, image_path: Optional[str], image_b64: Optional[str]) -> Dict:
    vectorizer, encoder, booster = load_artifacts()

    # features
    X_text = extract_text_features(vectorizer, text)
    img = _load_image_from_input(image_path, image_b64)
    img_vec = extract_image_features(img)
    X = fuse_features(X_text, img_vec)

    # xgboost: accept scipy CSR
    proba = booster.predict_proba(X)[0]  # (n_classes,)
    pred_idx = int(np.argmax(proba))
    pred_label = encoder.inverse_transform([pred_idx])[0]

    # top-3 (optional)
    top3_idx = np.argsort(proba)[::-1][:3].tolist()
    top3 = [
        {"label": encoder.inverse_transform([i])[0], "proba": float(proba[i])}
        for i in top3_idx
    ]

    return {
        "status": "ok",
        "predicted_label": pred_label,
        "probabilities": {encoder.inverse_transform([i])[0]: float(proba[i]) for i in range(len(proba))},
        "top3": top3,
    }

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Predict Rakuten (texte+image) with XGBoost fusion.")
    parser.add_argument("--text", required=True, help="Texte d'entrée")
    parser.add_argument("--image", default=None, help="Chemin de l'image (PNG/JPG)")
    parser.add_argument("--image_base64", default=None, help="Image encodée en base64 (optionnel)")
    parser.add_argument("--json", action="store_true", help="Imprimer strictement le JSON")
    args = parser.parse_args()

    result = predict_one(args.text, args.image, args.image_base64)
    out = json.dumps(result, ensure_ascii=False)
    print(out if args.json else f"\nPrediction\n----------\n{out}\n")

if __name__ == "__main__":
    main()
