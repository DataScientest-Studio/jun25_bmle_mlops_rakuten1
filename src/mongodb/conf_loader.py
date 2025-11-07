#!/usr/bin/env python3
"""
conf_loader.py
Utilitaire pour charger et compléter la configuration MongoDB via un fichier YAML.
Inclut une classe MongoConfLoader adaptée pour l'usage dans des projets multi-compose.
"""

import os
from typing import Any
import yaml

DEFAULT_CONF_PATH = "../../conf/mongodb.yaml"  # Chemin relatif depuis src/mongodb/
DEFAULT_MONGO_CONF = {
    "storage": {"dbPath": "/data/db"},
    "systemLog": {
        "destination": "file",
        "path": "/var/log/mongodb/mongod.log",
        "logAppend": True,
    },
    "net": {"port": 27017, "bindIp": "0.0.0.0"},
}


class MongoConfLoader:
    """
    Charge la configuration MongoDB depuis un fichier YAML,
    complète les clés manquantes grâce à une structure par défaut
    et fournit la config sous forme de dict ou JSON.
    """

    def __init__(
        self,
        conf_path: str = DEFAULT_CONF_PATH,
        defaults: dict[str, Any] = None,
    ):
        """
        Initialise le loader avec le chemin du fichier YAML et une structure par défaut.
        """
        self.conf_path = conf_path
        self.defaults = defaults or DEFAULT_MONGO_CONF

    def load_yaml_as_dict(self) -> dict[str, Any]:
        """
        Charge le YAML, fusionne avec la structure par défaut,
        et retourne la configuration complète sous forme de dict Python.
        """
        if os.path.exists(self.conf_path):
            with open(self.conf_path, "r", encoding="utf-8") as f:
                user_conf = yaml.safe_load(f) or {}
        else:
            user_conf = {}
        return self._deep_merge_dict(self.defaults, user_conf)

    @staticmethod
    def _deep_merge_dict(default: dict, override: dict) -> dict:
        """
        Fusionne récursivement deux dictionnaires.
        Les clés dans override remplacent celles dans default, récursivement.
        """
        result = default.copy()
        for key, value in override.items():
            # Fusion récursive si les valeurs sont elles-mêmes des dicts
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = MongoConfLoader._deep_merge_dict(result[key], value)
            else:
                result[key] = value
        return result

    def as_json(self) -> str:
        """
        Produit la configuration complète au format JSON.
        Pratique pour debug ou export.
        """
        import json

        config = self.load_yaml_as_dict()
        return json.dumps(config, indent=2, ensure_ascii=False)


# # Exemple d'utilisation
# if __name__ == "__main__":
#     loader = MongoConfLoader()
#     conf_dict = loader.load_yaml_as_dict()
#     print("Configuration fusionnée (dict):\n", conf_dict)
#     print("Configuration fusionnée (JSON):")
#     print(loader.as_json())
