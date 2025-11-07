import pandas as pd
import os
import io
from pymongo import MongoClient
from PIL import Image
from src.data.clean_text import clean_text
from src.mongodb.setup_database import connect_to_mongodb

# Configuration depuis variables d'environnement
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_ADMIN_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_ADMIN_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "changeme")
MONGO_DB_NAME = os.getenv("MONGO_INITDB_DATABASE", "mlops_rakuten")

IMAGE_SIZE = (224, 224)

connection_string = f"mongodb://{MONGO_ADMIN_USER}:{MONGO_ADMIN_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/admin"
#client = MongoClient(connection_string)
client = connect_to_mongodb()


# Dossiers d'entrée et de sortie
input_dir = os.path.join("data", "raw")
images_dir = os.path.join("data", "raw", "images", "images")
output_dir = os.path.join("data", "cleaned")
#input_dir = "/data/raw"
#images_dir = "/data/raw/images/images"
#output_dir = "/data/cleaned"

#client = connect_to_mongodb()
db = client[MONGO_DB_NAME]

# Chargement des fichiers CSV
X_train = pd.read_csv(os.path.join(input_dir, "X_train_update.csv"))
y_train = pd.read_csv(os.path.join(input_dir, "Y_train_CVw08PX.csv"))
X_test = pd.read_csv(os.path.join(input_dir, "X_test_update.csv"))

# Renommage de la première colonne en "id"
X_train.rename(columns={X_train.columns[0]: "id"}, inplace=True)
X_test.rename(columns={X_test.columns[0]: "id"}, inplace=True)
y_train.rename(columns={y_train.columns[0]: "id"}, inplace=True)

# Nettoyage des colonnes texte avec la fonction clean_text
X_train["designation"] = X_train["designation"].apply(clean_text)
X_test["designation"] = X_test["designation"].apply(clean_text)
X_train["description"] = X_train["description"].apply(clean_text)
X_test["description"] = X_test["description"].apply(clean_text)

# Sauvegarde des fichiers nettoyés
X_train.to_csv(os.path.join(output_dir, "X_train_cleaned.csv"), index=False)
X_test.to_csv(os.path.join(output_dir, "X_test_cleaned.csv"), index=False)
y_train.to_csv(os.path.join(output_dir, "Y_train_cleaned.csv"), index=False)

db.X_train.delete_many({}) 
db.X_test.delete_many({})
db.Y_train.delete_many({})

for _, row in X_train.iterrows():
    image_filename = str("image_" + str(row["imageid"] + "product_" + row["productid"]) + ".jpg")
    image_path = os.path.join(images_dir, "image_train", image_filename)
    if os.path.exists(image_path):
        # Ouvrir et redimensionner l'image avec PIL (comme avant)
        img = Image.open(image_path).convert("RGB").resize(IMAGE_SIZE)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        # Construire document à insérer (ajouter toutes colonnes du dataframe)
        doc = row.to_dict()
        doc["image_binary"] = img_bytes
#        doc["imageid"] = imageid  # remplace productid + imageid colonne séparée
#        doc.pop("productid", None)
        
        db.X_train_cleaned.insert_one(doc)
    else:
        print(f"Image non trouvée : {image_filename}")



db.X_train_cleaned.insert_many(X_train.to_dict("records"))
db.X_test_cleaned.insert_many(X_test.to_dict("records"))
db.Y_train_cleaned.insert_many(y_train.to_dict("records"))

client.close()
