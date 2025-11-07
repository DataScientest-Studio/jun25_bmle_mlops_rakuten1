#!/usr/bin/env python3
"""
write_mongodata.py
Script d'exemple pour se connecter à MongoDB, écrire un document et lire le résultat.
À placer dans src/data/. Utilise MongoConfLoader et MongoUtils du package src/mongodb.
Compatible Python 3.11+, structuré pour usage production ou prototypage.
"""

from datetime import datetime, timezone

# Imports des utilitaires dans src/mongodb/
from src.mongodb.conf_loader import MongoConfLoader
from src.mongodb.mongo_utils import MongoUtils

def main():
    """
    Etape 1 : charge la config Mongo
    Etape 2 : connecte à la base Mongo
    Etape 3 : insère et lit un document simple
    Etape 4 : ferme la connexion
    """
    # Charger la configuration depuis le YAML fusionné et compléter
    conf_loader = MongoConfLoader()

    # Connexion/context manager "with" assure ouverture/fermeture clean
    with MongoUtils(conf_loader=conf_loader) as mongo:
        # Insérer un document avec timestamp dans une collection dédiée
        result = mongo.db["data_log"].insert_one({"timestamp": datetime.now(timezone.utc)})
        print(f"Document inséré avec _id {result.inserted_id}")

        # Lire et afficher le dernier document inséré
        last_doc = mongo.db["data_log"].find_one(sort=[("timestamp", -1)])
        print("Dernier document dans 'data_log' :", last_doc)

if __name__ == "__main__":
    main()
