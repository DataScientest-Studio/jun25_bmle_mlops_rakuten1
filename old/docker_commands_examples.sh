# 1. Créer les dossiers nécessaires
# mkdir -p data/{raw,preprocessed,processed} models airflow/{dags,logs,plugins} config notebooks

# 2. Configurer l'environnement
# cp .env.example .env
# Modifier .env avec vos propres mots de passe

# 3. Build tous les containers
docker compose build

# 4. Démarrer tous les services
docker compose up -d

# 5. Vérifier l'état
docker compose ps

# 6. Voir les logs
docker compose logs -f

# 7. Arrêter tout
docker compose down

# 8. Reset complet (avec suppression des volumes)
docker compose down -v
