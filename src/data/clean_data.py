import html
import io
import os
import re
import warnings

import pandas as pd
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from PIL import Image
from tqdm.auto import tqdm

from src.mongodb.conf_loader import MongoConfLoader
from src.mongodb.utils import MongoUtils


warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

IMAGE_SIZE = (224, 224)


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = BeautifulSoup(text, "html.parser").get_text(" ")
    text = html.unescape(text)
    text = re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def clean_one_row(designation, description, image):
    designation = clean_text(designation)
    description = clean_text(description)
    img_byte_arr = io.BytesIO()
    image = image.convert("RGB").resize(IMAGE_SIZE)
    image.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    doc = {"designation": designation, "description": description, "image_binary": img_bytes}
    return doc


# Dossiers d'entrée et de sortie
# input_dir = os.path.join("data", "raw")
# images_dir = os.path.join("data", "raw", "images", "images")
# output_dir = os.path.join("data", "cleaned")
input_dir = "/app/data/raw"
images_dir = "/app/data/raw/images/images"
# output_dir = "/data/cleaned"

# Chargement des fichiers CSV
print("Chargement des fichiers CSV...")
X_train = pd.read_csv(os.path.join(input_dir, "X_train_update.csv"))
y_train = pd.read_csv(os.path.join(input_dir, "Y_train_CVw08PX.csv"))
X_test = pd.read_csv(os.path.join(input_dir, "X_test_update.csv"))

# Renommage de la première colonne en "id"
print("Renommage de la première colonne en 'id'...")
X_train.rename(columns={X_train.columns[0]: "id"}, inplace=True)
X_test.rename(columns={X_test.columns[0]: "id"}, inplace=True)
y_train.rename(columns={y_train.columns[0]: "id"}, inplace=True)

# Connexion/context manager "with" assure ouverture/fermeture clean
print("Connexion à MongoDB et insertion des données nettoyées...")
conf_loader = MongoConfLoader()
with MongoUtils(conf_loader=conf_loader, host="mongodb") as mongo:
    X_train_cleaned = mongo.db["X_train_cleaned"]
    X_test_cleaned = mongo.db["X_test_cleaned"]

    print("purge des collections existantes...")
    X_train_cleaned.delete_many({})
    X_test_cleaned.delete_many({})

    # Nettoyage et insertion des données d'entraînement
    for index, row in tqdm(
        X_train.head(10000).iterrows(),
        desc="Nettoyage et insertion X_train",
        total=len(X_train.head(10000)),
    ):
        image_filename = (
            "image_" + str(row["imageid"]) + "_product_" + str(row["productid"]) + ".jpg"
        )
        image_path = os.path.join(images_dir, "image_train", image_filename)
        if os.path.exists(image_path):
            img = Image.open(image_path)
            doc = clean_one_row(row["designation"], row["description"], Image.open(image_path))
            doc["id"] = row["id"]
            doc["prdtypecode"] = int(y_train.loc[index, "prdtypecode"])
            X_train_cleaned.insert_one(doc)

        else:
            print(f"Image non trouvée : {image_filename}")

    # Nettoyage et insertion des données de test
    for _, row in tqdm(
        X_test.head(1000).iterrows(),
        desc="Nettoyage et insertion X_test",
        total=len(X_test.head(1000)),
    ):
        image_filename = (
            "image_" + str(row["imageid"]) + "_product_" + str(row["productid"]) + ".jpg"
        )
        image_path = os.path.join(images_dir, "image_test", image_filename)
        if os.path.exists(image_path):
            img = Image.open(image_path)
            doc = clean_one_row(row["designation"], row["description"], Image.open(image_path))
            doc["id"] = row["id"]
            X_test_cleaned.insert_one(doc)

        else:
            print(f"Image non trouvée : {image_filename}")

# db.X_train_cleaned.insert_many(X_train.to_dict("records"))
# db.X_test_cleaned.insert_many(X_test.to_dict("records"))
# db.Y_train_cleaned.insert_many(y_train.to_dict("records"))


# Sauvegarde des fichiers nettoyés
# X_train.to_csv(os.path.join(output_dir, "X_train_cleaned.csv"), index=False)
# X_test.to_csv(os.path.join(output_dir, "X_test_cleaned.csv"), index=False)
# y_train.to_csv(os.path.join(output_dir, "Y_train_cleaned.csv"), index=False)
