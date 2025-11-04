# Build et démarrer MongoDB
docker compose build mongodb
docker compose up -d mongodb

# Voir les logs d'initialisation
docker compose logs -f mongodb

# Se connecter au shell MongoDB
docker compose exec mongodb mongosh -u admin -p changeme --authenticationDatabase admin

# Tester la connexion applicative
docker compose exec mongodb mongosh -u mlops_app -p mlops_app_password --authenticationDatabase mlops_rakuten

🌐 URLs des services

| Service            | URL                        | Credentials         |
| ------------------ | -------------------------- | ------------------- |
| API FastAPI        | http://localhost:8000      | -                   |
| API Docs (Swagger) | http://localhost:8000/docs | -                   |
| MLflow UI          | http://localhost:5000      | -                   |
| Airflow UI         | http://localhost:8080      | admin / admin       |
| Grafana            | http://localhost:3000      | admin / admin123    |
| Prometheus         | http://localhost:9090      | -                   |
| MinIO Console      | http://localhost:9001      | minio / minio123456 |
| MongoDB            | mongodb://localhost:27017  | admin / changeme123 |