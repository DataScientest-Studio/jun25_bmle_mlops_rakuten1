# 📦 Guide spécifique pour les bonnes pratiques Docker pour le projet

---

## 1 Comment développer en mode container

On attend pour faciliter la lisibité du projet et les developpements/depoiements de suivre une architecture type :

### Toutes les sources sont dans /src, avec des sous-dossiers correspondant à des composants du projet
.                   # racine du projet
.src/                # repertoires des sources python/ipny/etc.
|__ composant/      # decoupage par composant (data/models/report/etc.)
    |__ file.py
|___composant_n/
    |___ file_n.py

### Tous les fichiers Dockerfile sont réparties dans des sous-dossier composants

.docker
|__ composant/      # decoupage par composant (data/models/report/etc.)
    |__ Dockerfile
    |__ README.md
    |__ etc.
|___composant_n/
    |__ Dockerfile
    |__ README.md
    |__ etc.

.docker-compose.yml           # fichier docker de l'application, regroupe tous les services (composants) à lancer pour l'application
.docker-compose-composant.yml # fichier docker pour le composant

## 2 Docker Compose - Gestion multi-services

### Démarrer tous les services
docker compose up -d

### Démarrer avec un docker-compose spécifique
docker compose -f docker-compose-data.yml up -d

Cette ligne permet de lancer la creation du container de l'image spéfique contenu dans le docker-compose-data.yml.
Cela permet donc d'isoler dans une image précise un composant particulier et de créer le container afférent
On pourra par la suite dans un docker-compose.yml global au projet y faire référence directement via le yml du composant.

### Démarrer services spécifiques (exemples courants)
# Lancement depuis le docker-compose.yml des services souhaités
docker compose up -d api mongodb mlflow-server postgres minio
docker compose up -d ml-worker
docker compose up -d airflow-webserver airflow-scheduler airflow-postgres
# On lance depuis le fichier docker-compose-data des services extract et transform définis
docker compose -f docker-compose-data.yml up -d extract transform

### Build et rebuild
docker compose build
# build d'un service spécifique
docker compose build api
# Forcer le build complet, sans vérification de cache
docker compose build --no-cache ml-worker

### Gestion et maintenance
docker compose stop
docker compose stop api
docker compose restart api
docker compose down
docker compose down -v
docker compose exec api bash
docker compose exec ml-worker bash
docker compose logs -f api
docker compose logs -f ml-worker

### DOCKER (orchestration)
| Commande | Usage |
|----------|-------|
| `docker compose up -d` | Démarrer tous les services |
| `docker compose up -d api mongodb` | Démarrer services spécifiques |
| `docker compose logs -f <service>` | Voir logs en direct |
| `docker compose down -v` | Tout arrêter et reset |

## 🌐 URLs des services

| Service | URL | Credentials |
|---------|-----|-------------|
| API FastAPI | http://localhost:8000 | - |
| API Docs (Swagger) | http://localhost:8000/docs | - |
| MLflow UI | http://localhost:5000 | - |
| Airflow UI | http://localhost:8080 | admin / admin |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| MinIO Console | http://localhost:9001 | minio / minio123456 |
| MongoDB | mongodb://localhost:27017 | admin / changeme |

# Evolution dans la suite, Dockerfile optimisé !

Pour faire un build puis un run, de façon à avoir un container optimisé avec uniquement les ressources nécessaires.
Le container sera plus rapide à déployer et beaucoup plus rapide en execution.
On construit une fois, on deploie lors des runs.

# ============================================================================
# DOCKERFILE MULTI-STAGE OPTIMISÉ - Data Cleaning Worker
# ============================================================================
# Objectifs:
#   - Image finale ultra-légère (50-100 MB de moins)
#   - Temps de build optimisé avec cache Docker
#   - Aucun outil de compilation dans l'image de production
#   - Sécurité renforcée (utilisateur non-root)
#
# Architecture:
#   STAGE 1 (builder) → Compile et installe toutes les dépendances
#   STAGE 2 (runtime) → Copie uniquement les binaires compilés
# ============================================================================

# ════════════════════════════════════════════════════════════════════════════
# STAGE 1: BUILDER - Environnement de compilation
# ════════════════════════════════════════════════════════════════════════════
# Ce stage contient tous les outils nécessaires pour compiler les dépendances
# Python (gcc, headers, build-tools). Il sera JETÉ après la compilation.
# ════════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim AS builder

# Métadonnées du maintainer
LABEL stage="builder"
LABEL maintainer="MLOps Rakuten Team"

# Définir le répertoire de travail
WORKDIR /app

# ────────────────────────────────────────────────────────────────────────────
# Installation de l'outil uv (gestionnaire de paquets ultra-rapide)
# ────────────────────────────────────────────────────────────────────────────
# uv est 10-100x plus rapide que pip pour l'installation de paquets
# Il sera disponible dans ce stage uniquement
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ────────────────────────────────────────────────────────────────────────────
# Copie des fichiers nécessaires pour l'installation
# ────────────────────────────────────────────────────────────────────────────
# Ordre optimisé pour le cache Docker:
# 1. pyproject.toml (change rarement) → mis en cache
# 2. src/ (change souvent) → rebuild uniquement si modifié

# Copier la configuration du projet
COPY pyproject.toml ./

# Copier le code source (requis car pyproject.toml déclare 'src' comme package)
COPY src/ /app/src/

# ────────────────────────────────────────────────────────────────────────────
# Installation des dépendances Python
# ────────────────────────────────────────────────────────────────────────────
# Options utilisées:
#   --system        : Installe dans le Python système (pas de venv)
#   --no-cache      : Ne garde pas de cache local (réduit la taille)
#   -e              : Mode éditable (permet import from src.*)
#   .[etl]          : Installe le package avec l'extra 'etl' du pyproject.toml
#
# Résultat: Toutes les dépendances sont installées dans:
#   /usr/local/lib/python3.11/site-packages/
RUN uv pip install --system --no-cache -e .[etl]

# ────────────────────────────────────────────────────────────────────────────
# FIN DU STAGE BUILDER
# ────────────────────────────────────────────────────────────────────────────
# À ce stade, nous avons:
#   ✓ Python 3.11 + toutes les dépendances compilées
#   ✓ Le code source dans /app/src/
#   ✓ Les outils de build (gcc, headers, etc.) - QUI SERONT JETÉS
#
# Taille du stage builder: ~500-800 MB (car contient gcc, headers, etc.)
# ════════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════════
# STAGE 2: RUNTIME - Image finale de production
# ════════════════════════════════════════════════════════════════════════════
# Ce stage crée l'image FINALE qui sera déployée.
# Il ne contient QUE le strict nécessaire pour exécuter le code:
#   - Python runtime (sans outils de compilation)
#   - Dépendances compilées (copiées depuis le builder)
#   - Code source
# ════════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim AS runtime

# Métadonnées de l'image finale
LABEL maintainer="MLOps Rakuten Team"
LABEL description="Data Cleaning Worker - Production Image"
LABEL version="1.0"

# Définir le répertoire de travail
WORKDIR /app

# ────────────────────────────────────────────────────────────────────────────
# Copie sélective depuis le stage builder
# ────────────────────────────────────────────────────────────────────────────
# On copie UNIQUEMENT ce qui est nécessaire à l'exécution:
#   1. Les packages Python compilés (pandas, numpy, etc.)
#   2. Le code source de notre application

# Copier les dépendances Python installées (depuis le builder)
# Cela inclut: pandas, numpy, beautifulsoup4, pydantic, etc.
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copier le code source de l'application (depuis le builder)
COPY --from=builder /app/src /app/src

# ────────────────────────────────────────────────────────────────────────────
# Configuration de la sécurité - Utilisateur non-root
# ────────────────────────────────────────────────────────────────────────────
# Bonne pratique de sécurité: NE JAMAIS exécuter un container en root
# On crée un utilisateur dédié 'mluser' avec UID 1000

# Créer l'utilisateur 'mluser' et lui donner les droits sur /app
RUN useradd -m -u 1000 mluser && \
    chown -R mluser:mluser /app

# Basculer vers l'utilisateur non-root
# Toutes les commandes suivantes s'exécutent en tant que 'mluser'
USER mluser

# ────────────────────────────────────────────────────────────────────────────
# Point d'entrée de l'application
# ────────────────────────────────────────────────────────────────────────────
# Commande exécutée au démarrage du container
# Format exec (avec []) recommandé pour la gestion correcte des signaux (SIGTERM, etc.)
CMD ["python", "src/data/clean_data.py"]

# ════════════════════════════════════════════════════════════════════════════
# FIN DE L'IMAGE RUNTIME
# ════════════════════════════════════════════════════════════════════════════
# Image finale contient:
#   ✅ Python 3.11 runtime (~50 MB)
#   ✅ Dépendances compilées (~100-150 MB)
#   ✅ Code source (~1-5 MB)
#   ✅ Utilisateur non-root (sécurité)
#
# Image finale NE contient PAS:
#   ❌ gcc, make, build-essential
#   ❌ Headers de développement Python
#   ❌ Cache pip/uv
#   ❌ Fichiers temporaires de build
#
# Taille finale: ~150-250 MB (vs ~500-800 MB sans multi-stage)
# Gain: 50-70% de réduction de taille !
# ════════════════════════════════════════════════════════════════════════════


🚀 Commandes de lancement
1️⃣ Build et lancement avec docker-compose (RECOMMANDÉ)

bash
# ══════════════════════════════════════════════════════════════════════════
# Construction et lancement avec docker-compose --> Préférence !
# ══════════════════════════════════════════════════════════════════════════

# Build + lancement en mode attaché (voir les logs en temps réel)
docker compose -f docker-compose-etl.yml up --build

# Build + lancement en mode détaché (arrière-plan)
docker compose -f docker-compose-etl.yml up --build -d

# Voir les logs si lancé en mode détaché
docker compose -f docker-compose-etl.yml logs -f cleaning

# Arrêter le container
docker compose -f docker-compose-etl.yml down

# Rebuild complet (sans cache) + lancement
docker compose -f docker-compose-etl.yml build --no-cache
docker compose -f docker-compose-etl.yml up

2️⃣ Build manuel avec docker build

# ══════════════════════════════════════════════════════════════════════════
# Construction manuelle de l'image (depuis la racine du projet) --> Pour le savoir
# ══════════════════════════════════════════════════════════════════════════

# Build normal
docker build \
  -f docker/clean_data/Dockerfile \
  -t mlops-rakuten/clean-data:latest \
  .

# Build sans cache (force rebuild complet)
docker build \
  --no-cache \
  -f docker/clean_data/Dockerfile \
  -t mlops-rakuten/clean-data:latest \
  .

# Build avec affichage détaillé (debug)
docker build \
  --progress=plain \
  -f docker/clean_data/Dockerfile \
  -t mlops-rakuten/clean-data:latest \
  .

3️⃣ Lancement manuel avec docker run

bash
# ══════════════════════════════════════════════════════════════════════════
# Lancement manuel du container (après build) --> Pour le savoir
# ══════════════════════════════════════════════════════════════════════════

# Lancement avec volumes montés
docker run --rm \
  --name mlops-clean-data \
  -v "$(pwd)/data/raw:/app/data/raw:ro" \
  -v "$(pwd)/data/cleaned:/app/data/cleaned" \
  mlops-rakuten/clean-data:latest

# Lancement en mode interactif (pour debug)
docker run --rm -it \
  --name mlops-clean-data \
  -v "$(pwd)/data/raw:/app/data/raw:ro" \
  -v "$(pwd)/data/cleaned:/app/data/cleaned" \
  mlops-rakuten/clean-data:latest \
  bash

# Dans le container interactif, vérifier:
ls -la /app/data/raw/
python src/data/clean_data.py
exit

4️⃣ Inspection et debug

# ══════════════════════════════════════════════════════════════════════════
# Commandes d'inspection et debug
# ══════════════════════════════════════════════════════════════════════════

# Vérifier la taille des images (comparer builder vs runtime)
docker images | grep mlops-rakuten

# Inspecter l'image finale
docker inspect mlops-rakuten/clean-data:latest

# Voir l'historique des layers (identifier les plus lourds)
docker history mlops-rakuten/clean-data:latest

# Analyser la taille des layers avec dive (installer: https://github.com/wagoodman/dive)
dive mlops-rakuten/clean-data:latest

# Entrer dans un container en cours d'exécution
docker exec -it mlops-clean-data bash

# Vérifier les logs du container
docker logs mlops-clean-data

# Vérifier l'utilisation des ressources
docker stats mlops-clean-data

5️⃣ Nettoyage

# ══════════════════════════════════════════════════════════════════════════
# Nettoyage des ressources Docker
# ══════════════════════════════════════════════════════════════════════════

# Arrêter et supprimer le container
docker compose -f docker-compose-etl.yml down

# Supprimer l'image
docker rmi mlops-rakuten/clean-data:latest

# Nettoyer les images intermédiaires (builder stages)
docker image prune -f

# Nettoyer TOUT (containers arrêtés, images, volumes, cache)
docker system prune -a --volumes

| Aspect            | Dockerfile Simple                    | Dockerfile Multi-stage          |
| ----------------- | ------------------------------------ | ------------------------------- |
| Taille image      | ~500-800 MB                          | ~150-250 MB                     |
| Contenu           | Python + dépendances + gcc + headers | Python + dépendances uniquement |
| Sécurité          | Outils de compilation présents       | Aucun outil de compilation      |
| Temps build       | Moyen                                | Légèrement plus long (2 stages) |
| Temps déploiement | Lent (image lourde)                  | Rapide (image légère)           |
| Cache Docker      | Efficace                             | Très efficace (layers séparés)  |

✅ Workflow recommandé

# 1. Développement (build rapide avec cache)
docker compose -f docker-compose-etl.yml up --build

# 2. Test d'un changement de code (rebuild rapide)
docker compose -f docker-compose-etl.yml up --build

# 3. Production (build complet sans cache)
docker compose -f docker-compose-etl.yml build --no-cache
docker compose -f docker-compose-etl.yml up -d

# 4. Vérifier les logs
docker compose -f docker-compose-etl.yml logs -f cleaning

## Fichier docker-compose global avec les include pour les docker-compose-composant.yml

# ============================================================================
# DOCKER COMPOSE GLOBAL - Orchestration avec include
# ============================================================================
# Ce fichier référence les autres fichiers docker-compose-*.yml
# Avantages:
#   - Pas de duplication de code
#   - Chaque équipe maintient son propre fichier
#   - Le fichier global reste simple et lisible
#   - Les fichiers peuvent être testés indépendamment
#
# Usage:
#   docker compose up --build        # Lance TOUS les services
#   docker compose up cleaning       # Lance uniquement ETL
#   docker compose up api            # Lance API + MongoDB (dépendance)
# ============================================================================

# Inclure les fichiers de configuration des différents services
include:
  - docker-compose-etl.yml      # Service ETL
  - docker-compose-api.yml      # Service API
  - docker-compose-db.yml       # Service MongoDB

# Réseau partagé par tous les services
networks:
  default:
    name: mlops-network
    driver: bridge


Bien plus simple non !