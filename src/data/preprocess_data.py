import io
import os

import joblib
import numpy as np
import pandas as pd
import torch
from PIL import Image
from scipy import sparse
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from torch import nn
from torchvision import models, transforms
from tqdm.auto import tqdm

from src.mongodb.conf_loader import MongoConfLoader
from src.mongodb.utils import MongoUtils


class Preprocessor:
    def __init__(self, tfidf=None, batch_size=32):
        if tfidf is None:
            self.tfidf = joblib.load("data/processed/tfidf_vectorizer.joblib")
        else:
            self.tfidf = tfidf
        self.preprocess = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.resnet = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        self.resnet.fc = nn.Identity()
        self.batch_size = batch_size

    def preprocess_data(self, df: pd.DataFrame) -> tuple:
        X_tfidf = self.tfidf.transform(tqdm(df["text"], desc="Vectorisation TF-IDF"))

        self.resnet.eval().to(self.device)
        feats = []
        for i in tqdm(range(0, len(df), self.batch_size), desc="ResNet50 embeddings"):
            batch_tensors = []
            for image_binary in df["image_binary"][i : i + self.batch_size]:
                try:
                    img_byte_arr = io.BytesIO(image_binary)
                    img = Image.open(img_byte_arr)
                    x = self.preprocess(img).to(self.device)
                except Exception:
                    x = torch.zeros(3, 224, 224)  # image manquante/cassée
                batch_tensors.append(x)
            xb = torch.stack(batch_tensors).to(self.device)
            with torch.no_grad():
                emb = self.resnet(xb).cpu().numpy()  # (B, 2048, 1, 1) ou (B, 2048)
                emb = emb.reshape(emb.shape[0], -1)
            feats.append(emb)

        X_img = np.vstack(feats).astype(np.float32)

        return X_tfidf, X_img


# Dossiers d'entrée et de sortie
output_dir = os.path.join("data", "processed")
# print("result output dir:", output_dir)
# output_dir = "/data/processed"

# Recuperation des données depuis MongoDB
conf_loader = MongoConfLoader()
print("Connection à MongoDB...")
with MongoUtils(conf_loader=conf_loader, host="localhost") as mongo:
    print("Connection à MongoDB établie.")
    X_train_cleaned_col = mongo.db["X_train_cleaned"]
    X_test_cleaned_col = mongo.db["X_test_cleaned"]
    print("Recuperation des données de Train depuis MongoDB...")
    X_train_cursor = X_train_cleaned_col.find(
        {},
        {
            "_id": 0,
            "id": 1,
            "designation": 1,
            "description": 1,
            "prdtypecode": 1,
            "image_binary": 1,
        },
    )
    nb_docs_X_train = X_train_cleaned_col.count_documents({})
    X_train_data = []
    for doc in tqdm(X_train_cursor, total=nb_docs_X_train, desc="Chargement données Train"):
        X_train_data.append(doc)
    df_train = pd.DataFrame(X_train_data)
    print("Recuperation des données de Test depuis MongoDB...")
    X_test_cursor = X_test_cleaned_col.find(
        {},
        {
            "_id": 0,
            "id": 1,
            "designation": 1,
            "description": 1,
            "image_binary": 1,
        },
    )
    nb_docs_X_test = X_test_cleaned_col.count_documents({})

    X_test_data = []
    for doc in tqdm(X_test_cursor, total=nb_docs_X_test, desc="Chargement données Test"):
        X_test_data.append(doc)
    df_test = pd.DataFrame(X_test_data)

df_train["text"] = df_train["designation"].fillna("") + " " + df_train["description"].fillna("")
X = df_train[["text", "image_binary"]]
y = df_train["prdtypecode"].values

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y)

# Preparation TF-IDF
tfidf = TfidfVectorizer(
    max_features=20000,  # limite stricte
    ngram_range=(1, 2),  # mots simples + bi-grammes
    sublinear_tf=True,
    min_df=2,  # ignorer termes rares
)
tqdm.pandas(desc="TF-IDF vectorizer : Fitting and transforming Train")
# df_train["text"] = df_train["designation"].fillna("") + " " + df_train["description"].fillna("")
tfidf = tfidf.fit(tqdm(X_train["text"], desc="Fitting TF-IDF"))
joblib.dump(tfidf, "data/processed/tfidf_vectorizer.joblib")

preprocessor = Preprocessor(tfidf=tfidf, batch_size=32)
X_train_text, X_train_img = preprocessor.preprocess_data(X_train)
X_val_text, X_val_img = preprocessor.preprocess_data(X_val)

# X = hstack([X_tfidf, X_img])
# y = df_train["prdtypecode"].values

# X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y)

sparse.save_npz(os.path.join(output_dir, "X_train.npz"), X_train_text)
sparse.save_npz(os.path.join(output_dir, "X_val.npz"), X_val_text)
np.save(os.path.join(output_dir, "y_train.npy"), y_train)
np.save(os.path.join(output_dir, "y_val.npy"), y_val)
