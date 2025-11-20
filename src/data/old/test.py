import pandas as pd, re, html, os
from bs4 import BeautifulSoup
from tqdm.auto import tqdm

X = pd.read_csv(os.path.join("data", "raw", "X_train_update.csv"))
Y = pd.read_csv(os.path.join("data", "raw", "Y_train_CVw08PX.csv"), usecols=["prdtypecode"])
df = X.copy()
df["label"] = Y["prdtypecode"]

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = BeautifulSoup(text, "html.parser").get_text(" ")
    text = html.unescape(text)
    text = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text

tqdm.pandas(desc="🧹 Nettoyage texte")
df["text"] = (df["designation"].fillna("") + " " + df["description"].fillna("")).progress_apply(clean_text)

os.makedirs("data", exist_ok=True)
df[["productid","imageid","text","label"]].to_csv("data/X_train_prepro.csv", index=False)
print("✅ data/X_train_prepro.csv :", df.shape)

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from tqdm.auto import tqdm
import joblib, os
from scipy import sparse

# === 1️⃣ Chargement du texte nettoyé ===
print("📂 Lecture du CSV nettoyé...")
df = pd.read_csv("data/X_train_prepro.csv")
print(f"✅ Lignes : {len(df)}")

# === 2️⃣ TF-IDF (uniquement sur les mots) ===
print("🔤 Construction du TF-IDF (mots + bi-grammes)...")

tfidf = TfidfVectorizer(
    max_features=20000,      # limite stricte
    ngram_range=(1, 2),      # mots simples + bi-grammes
    sublinear_tf=True,
    min_df=2                 # ignorer termes rares
)

tqdm.pandas(desc="TF-IDF (mots)")
X_tfidf = tfidf.fit_transform(tqdm(df["text"], desc="Vectorisation TF-IDF"))
y = df["label"].values

print(f"✅ X_text_sparse: {X_tfidf.shape} | y: {y.shape}")

# === 3️⃣ Sauvegardes ===
os.makedirs("data/processed", exist_ok=True)

sparse.save_npz("data/processed/X_text_sparse.npz", X_tfidf)
joblib.dump(tfidf, "data/processed/tfidf_vectorizer.joblib")
import numpy as np
np.save("data/processed/y.npy", y)

print("💾 Sauvegardes :")
print(" - data/processed/X_text_sparse.npz")
print(" - data/processed/tfidf_vectorizer.joblib")
print(" - data/processed/y.npy")