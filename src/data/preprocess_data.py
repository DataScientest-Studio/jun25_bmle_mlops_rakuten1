import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import json

# Dossiers d'entrée et de sortie
input_dir = os.path.join("data", "cleaned")
output_dir = os.path.join("data", "preprocessed")
#input_dir = "/data/cleaned"
#output_dir = "/data/preprocessed"

# Chargement des fichiers CSV
X_train = pd.read_csv(os.path.join(input_dir, "X_train_cleaned.csv"))
y_train = pd.read_csv(os.path.join(input_dir, "Y_train_cleaned.csv"))
X_test = pd.read_csv(os.path.join(input_dir, "X_test_cleaned.csv"))

tfidf = TfidfVectorizer(
    max_features=20000,      # limite stricte
    ngram_range=(1, 2),      # mots simples + bi-grammes
    sublinear_tf=True,
    min_df=2                 # ignorer termes rares
)

X_train["text"] = (
    X_train["designation"].fillna("") + " " + X_train["description"].fillna("")
)
X_test["text"] = (
    X_test["designation"].fillna("") + " " + X_test["description"].fillna("")
)

print("Fitting TF-IDF vectorizer Train...")
tfidf_x_train = tfidf.fit_transform(X_train["text"]).toarray().tolist()
print("Fitting TF-IDF Train complete...")
#print("OK")
#"""
print("Fitting TF-IDF vectorizer Test...")
tfidf_x_test = tfidf.transform(X_test["text"]).toarray().tolist()
print("TF-IDF transformation Test complete.")
json_x_train = []
for idx, prod_id, img_id, vect in zip(X_train["id"], X_train["productid"], X_train["imageid"], tfidf_x_train):
    json_x_train.append({
        "id": idx,
        "tfidf": vect,
        "productid": prod_id,
        "imageid": img_id
    })

json_x_test = []
for idx, prod_id, img_id, vect in zip(X_test["id"], X_test["productid"], X_test["imageid"], tfidf_x_test):
    json_x_test.append({
        "id": idx,
        "tfidf": vect,
        "productid": prod_id,
        "imageid": img_id
    })

with open(os.path.join(output_dir, "X_train_preprocessed.json"), "w") as f:
    json.dump(json_x_train, f)

with open(os.path.join(output_dir, "X_test_preprocessed.json"), "w") as f:
    json.dump(json_x_test, f)
#"""