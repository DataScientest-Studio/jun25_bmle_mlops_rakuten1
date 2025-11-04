import pandas as pd
import os
from src.data.clean_text import clean_text

# Dossiers d'entrée et de sortie
input_dir = os.path.join("data", "raw")
output_dir = os.path.join("data", "cleaned")

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
