#!/bin/bash
set -e

echo "=========================================="
echo "MongoDB Initialization Script - MLOps Rakuten"
echo "=========================================="

# Variables d'environnement (définies dans docker-compose.yml)
MONGO_ADMIN_USER="${MONGO_INITDB_ROOT_USERNAME:-admin}"
MONGO_ADMIN_PASSWORD="${MONGO_INITDB_ROOT_PASSWORD:-changeme}"
MONGO_DB_NAME="${MONGO_INITDB_DATABASE:-mlops_rakuten}"

echo "Creating database: ${MONGO_DB_NAME}"

# Connexion en tant qu'admin et création de la base de données
mongosh --quiet <<EOF

// Se connecter à la base admin
use admin;

// Vérifier que l'admin existe
print("Admin user: ${MONGO_ADMIN_USER}");

// Basculer vers la base de données applicative
use ${MONGO_DB_NAME};

// Créer les collections principales
db.createCollection("users");
db.createCollection("models");
db.createCollection("predictions");
db.createCollection("experiments");
db.createCollection("data_cleaned");
db.createCollection("data_preprocessed");
db.createCollection("training_jobs");
db.createCollection("api_logs");

print("Collections created successfully");

// Créer un utilisateur applicatif avec privilèges limités
db.createUser({
    user: "mlops_app",
    pwd: "mlops_app_password",
    roles: [
        {
            role: "readWrite",
            db: "${MONGO_DB_NAME}"
        },
        {
            role: "dbAdmin",
            db: "${MONGO_DB_NAME}"
        }
    ]
});

print("Application user 'mlops_app' created successfully");

// Créer un utilisateur read-only pour analytics/reporting
db.createUser({
    user: "mlops_readonly",
    pwd: "mlops_readonly_password",
    roles: [
        {
            role: "read",
            db: "${MONGO_DB_NAME}"
        }
    ]
});

print("Read-only user 'mlops_readonly' created successfully");

// Créer des indexes de base pour performances
db.users.createIndex({ "email": 1 }, { unique: true, name: "idx_users_email" });
db.users.createIndex({ "username": 1 }, { unique: true, name: "idx_users_username" });
db.users.createIndex({ "created_at": -1 }, { name: "idx_users_created" });

db.models.createIndex({ "model_id": 1 }, { unique: true, name: "idx_models_id" });
db.models.createIndex({ "name": 1, "version": 1 }, { name: "idx_models_name_version" });
db.models.createIndex({ "created_at": -1 }, { name: "idx_models_created" });
db.models.createIndex({ "status": 1 }, { name: "idx_models_status" });

db.predictions.createIndex({ "model_id": 1 }, { name: "idx_predictions_model" });
db.predictions.createIndex({ "timestamp": -1 }, { name: "idx_predictions_timestamp" });
db.predictions.createIndex({ "user_id": 1 }, { name: "idx_predictions_user" });

db.experiments.createIndex({ "experiment_id": 1 }, { unique: true, name: "idx_experiments_id" });
db.experiments.createIndex({ "name": 1 }, { name: "idx_experiments_name" });
db.experiments.createIndex({ "created_at": -1 }, { name: "idx_experiments_created" });
db.experiments.createIndex({ "status": 1 }, { name: "idx_experiments_status" });

//db.datasets.createIndex({ "dataset_id": 1 }, { unique: true, name: "idx_datasets_id" });
//db.datasets.createIndex({ "name": 1 }, { name: "idx_datasets_name" });
//db.datasets.createIndex({ "created_at": -1 }, { name: "idx_datasets_created" });

db.training_jobs.createIndex({ "job_id": 1 }, { unique: true, name: "idx_jobs_id" });
db.training_jobs.createIndex({ "status": 1 }, { name: "idx_jobs_status" });
db.training_jobs.createIndex({ "created_at": -1 }, { name: "idx_jobs_created" });
db.training_jobs.createIndex({ "model_id": 1 }, { name: "idx_jobs_model" });

db.api_logs.createIndex({ "timestamp": -1 }, { expireAfterSeconds: 2592000, name: "idx_logs_ttl" });
db.api_logs.createIndex({ "endpoint": 1 }, { name: "idx_logs_endpoint" });
db.api_logs.createIndex({ "status_code": 1 }, { name: "idx_logs_status" });

print("Basic indexes created successfully");

EOF

echo "MongoDB initialization completed successfully!"
echo "Database: ${MONGO_DB_NAME}"
echo "Users created: mlops_app (readWrite), mlops_readonly (read)"
echo "=========================================="
