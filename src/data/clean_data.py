import io
import os

import pandas as pd
from PIL import Image

from src.data.clean_text import clean_text
from src.mongodb.conf_loader import MongoConfLoader
from src.mongodb.utils import MongoUtils
from tqdm.auto import tqdm


IMAGE_SIZE = (224, 224)


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
input_dir = os.path.join("data", "raw")
images_dir = os.path.join("data", "raw", "images", "images")
output_dir = os.path.join("data", "cleaned")
# input_dir = "/data/raw"
# images_dir = "/data/raw/images/images"
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
with MongoUtils(conf_loader=conf_loader) as mongo:
    db = mongo.db["mlops_rakuten"]
    print("purge des collections existantes...")
    db.X_train_cleaned.delete_many({})
    db.X_test_cleaned.delete_many({})
    db.Y_train_cleaned.delete_many({})

    for _, row in tqdm(
        X_train.iterrows(),
        desc="Nettoyage et insertion X_train",
        total=len(X_train),
    ):
        image_filename = (
            "image_" + str(row["imageid"]) + "_product_" + str(row["productid"]) + ".jpg"
        )
        image_path = os.path.join(images_dir, "image_train", image_filename)
        if os.path.exists(image_path):
            img = Image.open(image_path)
            #            print("Image size:", img.size)
            doc = clean_one_row(row["designation"], row["description"], Image.open(image_path))
            doc["id"] = row["id"]
            #            print("Doc keys:", doc.keys())
            #            print("Doc image_binary size:", len(doc["image_binary"]))
            db.X_train_cleaned.insert_one(doc)
        #            print(db.X_train_cleaned.count_documents({}))

        else:
            print(f"Image non trouvée : {image_filename}")

    print("Taille de la collection X_train_cleaned :", db.X_train_cleaned.count_documents({}))
    result = db.X_train_cleaned.find({}).limit(3)
    for doc in result:
        print("Document ID:", doc["id"])
        img_bytes = doc["image_binary"]
        img_byte_arr = io.BytesIO(img_bytes)
        img = Image.open(img_byte_arr)
        img.show()


# db.X_train_cleaned.insert_many(X_train.to_dict("records"))
# db.X_test_cleaned.insert_many(X_test.to_dict("records"))
# db.Y_train_cleaned.insert_many(y_train.to_dict("records"))


# Sauvegarde des fichiers nettoyés
# X_train.to_csv(os.path.join(output_dir, "X_train_cleaned.csv"), index=False)
# X_test.to_csv(os.path.join(output_dir, "X_test_cleaned.csv"), index=False)
# y_train.to_csv(os.path.join(output_dir, "Y_train_cleaned.csv"), index=False)
