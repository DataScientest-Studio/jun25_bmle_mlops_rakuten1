#!/usr/bin/env python3
"""
mongo_utils.py
Utilitaire pour manipuler MongoDB en Python.
La classe MongoUtils utilise MongoConfLoader pour la configuration dynamique.
Docstring et commentaires exhaustifs, compatible Python 3.11+, PEP8/Ruff.
"""

import os
from typing import Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from .conf_loader import MongoConfLoader  # Adapter l'import si besoin


class MongoUtils:
    """
    Classe d'aide pour la connexion et les opérations sur MongoDB.
    Accepte un objet MongoConfLoader pour charger la conf YAML.
    """

    def __init__(
        self,
        conf_loader: MongoConfLoader = None,
        db_name: str | None = None,
        admin_user: str | None = None,
        admin_pass: str | None = None,
        host: str | None = None,
        port: int | None = None,
    ):
        """
        Initialise le client MongoDB avec configuration prioritaire :
        - paramètres explicites > config YAML via conf_loader > variables d'environnement > défaut hardcodé.
        """
        self.conf_loader = conf_loader or MongoConfLoader()
        self.config = self.conf_loader.load_yaml_as_dict()

        # Résolution des paramètres de connexion (priorité décroissante)
        self.mongo_host = host or self.config.get("net", {}).get("bindIp", "localhost")
        self.mongo_port = port or self.config.get("net", {}).get("port", 27017)
        self.mongo_admin_user = (
            admin_user or os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
        )
        self.mongo_admin_password = (
            admin_pass or os.getenv("MONGO_INITDB_ROOT_PASSWORD", "changeme")
        )
        self.mongo_db_name = (
            db_name or os.getenv("MONGO_INITDB_DATABASE", "mlops_rakuten")
        )
        self.client = None
        self.db = None

    def connect(self) -> Any:
        """
        Établit la connexion MongoDB à partir des différents paramètres de configuration.
        Retourne : instance de la base de données MongoDB sélectionnée.
        """
        uri = (
            f"mongodb://{self.mongo_admin_user}:{self.mongo_admin_password}"
            f"@{self.mongo_host}:{self.mongo_port}/admin"
        )
        self.client = MongoClient(uri)
        self.db = self.client[self.mongo_db_name]
        return self.db

    def close(self) -> None:
        """
        Ferme proprement la connexion client.
        """
        if self.client is not None:
            self.client.close()

    def server_status(self) -> dict[str, Any]:
        """
        Effectue une commande `serverStatus` pour obtenir le timestamp serveur et autres méta-infos.
        Retourne : dict avec le résultat MongoDB.
        """
        if self.db is not None:
            return self.db.command("serverStatus")
        raise RuntimeError("Base Mongo non connectée (utiliser connect() ou le context manager).")

    def __enter__(self) -> "MongoUtils":
        """
        Prise en charge du context manager (`with`), connecte automatiquement.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Quitte proprement le context manager, ferme la connexion si requise.
        """
        self.close()


# # Exemple d’utilisation complet
# if __name__ == "__main__":
#     # Créer un chargeur de conf Mongo, qui va lire/confirmer/compléter la conf YAML
#     conf_loader = MongoConfLoader()
#     config = conf_loader.load_yaml_as_dict()
#     print("Configuration MongoDB chargée :")
#     print(config)

#     # Utiliser MongoUtils pour se connecter, exécuter une requête simple, puis fermer
#     with MongoUtils(conf_loader=conf_loader) as mongo:
#         # Requête : afficher la date/heure serveur
#         status = mongo.server_status()
#         print("Heure serveur rapportée par MongoDB :")
#         print(status["localTime"])
#     # Connexion automatiquement fermée hors du with
