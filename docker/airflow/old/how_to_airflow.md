📝 Explication de l'architecture Airflow
# Trois services Airflow :

    airflow-init (run once)

        S'exécute une seule fois au démarrage

        Initialise la base de données (airflow db upgrade)

        Crée l'utilisateur admin

        Se termine après l'initialisation (restart: "no")

        Les autres services attendent sa complétion (condition: service_completed_successfully)

    airflow-webserver (UI)

        Interface web Airflow

        Port 8080

        Dépend de airflow-init pour s'assurer que la DB est prête

    airflow-scheduler (orchestrateur)

        Planifie et exécute les DAGs

        Dépend aussi de airflow-init

🚀 Commandes de démarrage

bash
# Créer les dossiers nécessaires
mkdir -p airflow/{dags,logs,plugins}

# Démarrer Airflow (init se lancera automatiquement en premier)
docker compose up -d airflow-webserver airflow-scheduler

# Voir les logs d'initialisation
docker compose logs airflow-init

# Accéder à l'UI Airflow
# http://localhost:8080
# User: admin / Password: admin

💡 Pourquoi cette architecture ?

✅ Séparation des responsabilités - Init séparé du runtime
✅ Idempotent - Peut être relancé sans problème
✅ Pas de race condition - webserver/scheduler attendent l'init
✅ Pas de surcharge entrypoint - Utilise les entrypoints natifs d'Airflow