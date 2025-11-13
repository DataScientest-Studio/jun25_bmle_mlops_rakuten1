import html
import io
import math
import os
import re
import warnings
from datetime import datetime

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


def clean_data(
    input_dir="/app/data/raw", images_dir="/app/data/raw/images/images", nbre_lignes=1000
):
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
    mongo_host = os.getenv("MONGO_HOST", "localhost")
    with MongoUtils(conf_loader=conf_loader, host=mongo_host) as mongo:
        X_train_cleaned = mongo.db["X_train_cleaned"]
        X_test_cleaned = mongo.db["X_test_cleaned"]

        print("purge des collections existantes...")
        X_train_cleaned.delete_many({})
        X_test_cleaned.delete_many({})

        # Nettoyage et insertion des données d'entraînement
        nbre_lignes = len(X_train) if nbre_lignes is None else nbre_lignes
        for index, row in tqdm(
            X_train.head(nbre_lignes).iterrows(),
            desc="Nettoyage et insertion X_train",
            total=len(X_train.head(nbre_lignes)),
        ):
            image_filename = (
                "image_" + str(row["imageid"]) + "_product_" + str(row["productid"]) + ".jpg"
            )
            image_path = os.path.join(images_dir, "image_train", image_filename)
            if os.path.exists(image_path):
                img = Image.open(image_path)
                doc = clean_one_row(row["designation"], row["description"], img)
                doc["id"] = row["id"]
                doc["prdtypecode"] = int(y_train.loc[index, "prdtypecode"])
                X_train_cleaned.insert_one(doc)

            else:
                print(f"Image non trouvée : {image_filename}")

        # Nettoyage et insertion des données de test
        for _, row in tqdm(
            X_test.head(nbre_lignes).iterrows(),
            desc="Nettoyage et insertion X_test",
            total=len(X_test.head(nbre_lignes)),
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


def calcul_lignes_a_lire(date_lancement: str) -> int:
    """
    Calcule le nombre de lignes à lire dans un fichier de données en fonction de la date de lancement.

    La fonction interpolle linéairement entre 1000 lignes le 13 novembre 2025
    et 85000 lignes le 13 décembre 2025.
    Si la date fournie est avant le 13 novembre, retourne 1000.
    Si elle est après le 13 décembre, retourne 85000.

    Arguments:
    date_lancement -- chaîne au format 'YYYY-MM-DD' représentant la date du jour de lancement.

    Retour:
    Le nombre entier de lignes à lire correspondant à la date donnée.
    """

    lignes_min = 1000
    lignes_max = 85000
    date_debut = datetime(2025, 11, 15)
    date_fin = datetime(2025, 12, 13)
    date_actuelle = datetime.strptime(date_lancement, "%Y-%m-%d")
    jours_total = (date_fin - date_debut).days
    jours_actuel = (date_actuelle - date_debut).days

    if jours_actuel < 0:
        return lignes_min
    elif jours_actuel >= jours_total:
        return lignes_max

    lignes_a_lire = lignes_min + ((lignes_max - lignes_min) * jours_actuel / jours_total)
    return math.ceil(lignes_a_lire)


if __name__ == "__main__":
    # Dossiers d'entrée et de sortie
    input_dir = "/app/data/raw"
    images_dir = "/app/data/raw/images/images"
    nbre_lignes = 1000
    clean_data(input_dir=input_dir, images_dir=images_dir, nbre_lignes=nbre_lignes)
