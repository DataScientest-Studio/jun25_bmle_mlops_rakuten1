#!/usr/bin/env python3
"""
MongoDB Advanced Setup Script - MLOps Rakuten
Setup avancé avec validation, données de test, et configuration optimisée
"""

import os
import json
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, OperationFailure
from datetime import datetime, timezone

# Configuration depuis variables d'environnement
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_ADMIN_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_ADMIN_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "changeme")
MONGO_DB_NAME = os.getenv("MONGO_INITDB_DATABASE", "mlops_rakuten")

def connect_to_mongodb():
    """Connexion à MongoDB en tant qu'admin"""
    connection_string = f"mongodb://{MONGO_ADMIN_USER}:{MONGO_ADMIN_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/admin"
    client = MongoClient(connection_string)
    return client

def load_indexes_from_json():
    """Charge les définitions d'indexes depuis le fichier JSON"""
    indexes_file = "/docker-entrypoint-initdb.d/indexes.json"
    if os.path.exists(indexes_file):
        with open(indexes_file, 'r') as f:
            return json.load(f)
    return {}

def create_advanced_indexes(db, indexes_config):
    """Crée des indexes avancés depuis la config JSON"""
    print("Creating advanced indexes from JSON configuration...")
    
    for collection_name, indexes in indexes_config.items():
        if collection_name not in db.list_collection_names():
            print(f"  Skipping {collection_name} (collection doesn't exist)")
            continue
            
        collection = db[collection_name]
        for index in indexes:
            try:
                index_keys = [(k, v) for k, v in index["keys"].items()]
                index_options = index.get("options", {})
                collection.create_index(index_keys, **index_options)
                print(f"  ✓ Created index on {collection_name}: {index['keys']}")
            except Exception as e:
                print(f"  ✗ Failed to create index on {collection_name}: {e}")

def insert_sample_data(db):
    """Insère des données de test pour validation"""
    print("Inserting sample data for testing...")
    
    # Sample user
    try:
        db.users.insert_one({
            "username": "admin_test",
            "email": "admin@mlops-rakuten.com",
            "full_name": "Administrator Test",
            "role": "admin",
            "created_at": datetime.now(timezone.utc),
            "is_active": True
        })
        print("  ✓ Sample user created")
    except DuplicateKeyError:
        print("  ⚠ Sample user already exists")

    # Sample model metadata
    try:
        db.models.insert_one({
            "model_id": "model_test_001",
            "name": "Test Classification Model",
            "version": "1.0.0",
            "type": "classification",
            "framework": "pytorch",
            "status": "active",
            "metrics": {
                "accuracy": 0.95,
                "f1_score": 0.93
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        })
        print("  ✓ Sample model created")
    except DuplicateKeyError:
        print("  ⚠ Sample model already exists")

def validate_setup(db):
    """Valide que tout est correctement configuré"""
    print("\nValidating database setup...")
    
    # Vérifier les collections
    expected_collections = ["users", "models", "predictions", "experiments", 
                          "datasets", "training_jobs", "api_logs"]
    existing_collections = db.list_collection_names()
    
    for col in expected_collections:
        if col in existing_collections:
            count = db[col].count_documents({})
            print(f"  ✓ Collection '{col}' exists ({count} documents)")
        else:
            print(f"  ✗ Collection '{col}' missing")
    
    # Vérifier les indexes
    print("\nIndexes validation:")
    for col_name in ["users", "models", "predictions"]:
        if col_name in existing_collections:
            indexes = list(db[col_name].list_indexes())
            print(f"  {col_name}: {len(indexes)} indexes")

def master():
    """Point d'entrée principal"""
    print("=" * 50)
    print("MongoDB Advanced Setup - MLOps Rakuten")
    print("=" * 50)
    
    try:
        # Connexion
        client = connect_to_mongodb()
        db = client[MONGO_DB_NAME]
        print(f"Connected to database: {MONGO_DB_NAME}")
        
        # Charger et créer les indexes avancés
        indexes_config = load_indexes_from_json()
        if indexes_config:
            create_advanced_indexes(db, indexes_config)
        
        # Insérer des données de test
        insert_sample_data(db)
        
        # Valider le setup
        validate_setup(db)
        
        print("\n" + "=" * 50)
        print("✓ Advanced setup completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        raise
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    master()
