mlops-rakuten/
├── docker-compose.yml                    # ← Fichier principal téléchargé
├── .env                                  # ← Copier depuis .env.example
├── .env.example                          # ← Template configuration
├── pyproject.toml                        # ← Dépendances Python
├── README.md
├── .gitignore
│
├── docker/                               # Dockerfiles
│   ├── api/
│   │   └── Dockerfile
│   ├── ml/
│   │   └── Dockerfile
│   ├── mlflow/
│   │   ├── Dockerfile
│   │   └── entrypoint.sh
│   ├── airflow/
│   │   ├── Dockerfile
│   │   └── init-airflow.sh
│   └── mongodb/
│       ├── Dockerfile
│       ├── init-mongodb.sh
│       ├── setup-database.py
│       ├── indexes.json
│       └── mongod.yaml
│
├── src/                                  # Code source Python
│   ├── __init__.py
│   ├── master.py                          # FastAPI entrypoint
│   ├── api/
│   ├── ml/
│   └── utils/
│
├── data/                                 # Données (montées dans ml-worker)
│   ├── raw/
│   ├── preprocessed/
│   └── processed/
│
├── models/                               # Modèles ML sauvegardés
│
├── notebooks/                            # Jupyter notebooks
│
├── airflow/                              # Airflow DAGs et config
│   ├── dags/
│   ├── logs/
│   └── plugins/
│
├── config/                               # Configurations
│   ├── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       └── datasources/
│
└── tests/                                # Tests unitaires
    ├── test_api.py
    └── test_ml.py
