import os

import joblib
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from tqdm.auto import tqdm

from src.mongodb.conf_loader import MongoConfLoader
from src.mongodb.utils import MongoUtils


# Dossiers d'entrée et de sortie
output_dir = os.path.join("data", "processed")
# input_dir = "/data/cleaned"
# output_dir = "/data/preprocessed"

tfidf = TfidfVectorizer(
    max_features=20000,  # limite stricte
    ngram_range=(1, 2),  # mots simples + bi-grammes
    sublinear_tf=True,
    min_df=2,  # ignorer termes rares
)
conf_loader = MongoConfLoader()
with MongoUtils(conf_loader=conf_loader) as mongo:
    X_train_cleaned_col = mongo.db["X_train_cleaned"]
    X_test_cleaned_col = mongo.db["X_test_cleaned"]

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

    tqdm.pandas(desc="TF-IDF vectorizer : Fitting and transforming Train")
    df_train["text"] = df_train["designation"].fillna("") + " " + df_train["description"].fillna("")
    tfidf = tfidf.fit(tqdm(df_train["text"], desc="Vectorisation TF-IDF"))

    joblib.dump(tfidf, "data/processed/tfidf_vectorizer.joblib")

# print("OK")
"""
    y = df_train["prdtypecode"].values
    X_train, X_val, y_train, y_val = train_test_split(
        X_tfidf, y, test_size=0.2, stratify=y
    )
    sparse.save_npz("data/processed/X_text_sparse.npz", X_tfidf)


print("Fitting TF-IDF vectorizer Test...")
tfidf_x_test = tfidf.transform(X_test["text"]).toarray().tolist()
print("TF-IDF transformation Test complete.")
json_x_train = []
for idx, prod_id, img_id, vect in zip(
    X_train["id"], X_train["productid"], X_train["imageid"], tfidf_x_train
):
    json_x_train.append({"id": idx, "tfidf": vect, "productid": prod_id, "imageid": img_id})

json_x_test = []
for idx, prod_id, img_id, vect in zip(
    X_test["id"], X_test["productid"], X_test["imageid"], tfidf_x_test
):
    json_x_test.append({"id": idx, "tfidf": vect, "productid": prod_id, "imageid": img_id})

with open(os.path.join(output_dir, "X_train_preprocessed.json"), "w") as f:
    json.dump(json_x_train, f)

with open(os.path.join(output_dir, "X_test_preprocessed.json"), "w") as f:
    json.dump(json_x_test, f)
"""
