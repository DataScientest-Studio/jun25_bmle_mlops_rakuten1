Project Name
==============================

This project is a starting Pack for MLOps projects based on the subject "movie_recommandation". It's not perfect so feel free to make some modifications on it.

Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── logs               <- Logs from training and predicting
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   ├── visualization  <- Scripts to create exploratory and results oriented visualizations
    │   │   └── visualize.py
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>


# 🚀 Projet MLOps - Pipeline de Machine Learning en Production

## 📋 Informations du Projet

**Sujet :** Mise en place d'un pipeline MLOps complet avec microservices, orchestration et monitoring pour rakuten

**Équipe :**
- Marc - [marc@example.com](mailto:marc@example.com)
- Pascal - [pascal@example.com](mailto:pascal@example.com)
- Clément - [clement@example.com](mailto:clement@example.com)
- Sébastien - [sebastien@example.com](mailto:sebastien@example.com)

**Liens du Projet :**
- 📊 [Trello - Gestion du projet](https://trello.com/votre-board)
- 💻 [GitHub - Dépôt Git](https://github.com/votre-repo)

---

## Phase 1 : Fondations
**Deadline : 12 Novembre**

### Tâches

1. Définir les objectifs du projet et établir une première roadmap
2. Mettre en place un environnement de développement reproductible
3. Collecter et pré-traiter les données
4. Créer une base de données (SQL ou noSQL)
5. Stocker les données via un script Python à exécuter une seule fois pour l'instant
6. Construire et évaluer un modèle ML de base
7. Créer deux scripts Python (`training.py` & `predict.py`)
8. Implémenter une API d'inférence simple
9. Créer 2 endpoints (`training/` & `predict/`)

---

## Phase 2 : Microservices, Suivi & Versionning
**Deadline : 18 Novembre**

### Tâches

10. Mettre en place le suivi d'expériences avec MLflow
11. Ajouter le code de logging MLflow dans le script d'entraînement
12. Implémenter le versionning des données & modèles avec MLflow Registry
13. Comparer les performances après chaque entraînement et marquer le meilleur modèle dans MLflow
14. À la fin du script d'entraînement (ou plus tard avec Airflow, voir schéma n°1), charger la version précédente et comparer avec la nouvelle version entraînée

---

## Phase 3 : Orchestration & Déploiement
**Deadline : 28 Novembre**

### Tâches

15. Découper l'application en microservices Docker et concevoir une orchestration simple avec docker-compose
16. Développer la mise à jour automatique du modèle et des composants avec entraînement planifié : script cron ou Jenkins/Airflow (plus complexe)
17. **(OPTIONNEL)** Implémenter des tests unitaires (quelques cas d'exemples suffisent pour les tests CI/CD)
18. **(OPTIONNEL)** Créer un pipeline CI/CD avec GitHub Actions :
    - `ci.yaml` → Linter + Tests unitaires + Build images Docker
    - `release.yaml` → Linter + Tests unitaires + Build & Déploiement des images sur DockerHub
19. **(OPTIONNEL)** Optimiser et sécuriser l'API : Authentification de base ou OAuth2
20. **(OPTIONNEL)** Implémenter la scalabilité avec Kubernetes

---

## Phase 4 : Monitoring & Maintenance *(OPTIONNEL)*
**Deadline : 9 Décembre**

### Tâches

21. Mettre en place un suivi des performances avec Prometheus/Grafana
22. Implémenter la détection de dérive avec Evidently
23. Développer la mise à jour automatique du modèle et des composants avec entraînement déclenché : webhook Grafana ou Evidently

---

## Phase 5 : Frontend
**Deadline : 16 Décembre**

### Tâches

24. Créer une application Streamlit simple pour interagir avec l'API et effectuer des prédictions
25. Finaliser la documentation technique dans le repo

---

## 📅 Roadmap

05 Nov 12 Nov 19 Nov 29 Nov 10 Déc 17 Déc
|==================|==================|==================|==================|==================|
└─ Phase 1 ────────┘ │ │ │ │
Fondations │ │ │ │
└─ Phase 2 ────────┘ │ │ │
Microservices │ │ │
Suivi & Versionning │ │ │
└─ Phase 3 ────────┘ │ │
Orchestration │ │
& Déploiement │ │
└─ Phase 4 ───────┘ │
Monitoring │
& Maintenance │
(OPTIONNEL) │
└─ Phase 5 ───────┘
Frontend

text

### Planning détaillé

| Phase | Description | Date de début | Date de fin | Durée |
|-------|-------------|---------------|-------------|-------|
| **Phase 1** | Fondations | 05 Nov | 12 Nov | 8 jours |
| **Phase 2** | Microservices, Suivi & Versionning | 13 Nov | 18 Nov | 6 jours |
| **Phase 3** | Orchestration & Déploiement | 19 Nov | 28 Nov | 10 jours |
| **Phase 4** | Monitoring & Maintenance *(OPTIONNEL)* | 29 Nov | 09 Déc | 11 jours |
| **Phase 5** | Frontend | 10 Déc | 16 Déc | 7 jours |

---

## 📝 Notes

- Les tâches marquées **(OPTIONNEL)** peuvent être réalisées selon la disponibilité et les priorités de l'équipe
- Chaque phase doit être validée avant de passer à la suivante
- Les jalons intermédiaires doivent faire l'objet d'une revue d'équipe

---

**Dernière mise à jour :** 04 Novembre 2025
