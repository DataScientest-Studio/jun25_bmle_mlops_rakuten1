# 📦 Docker pour le projet

## 1. Structure du projet

On attend pour faciliter la lisibité du projet et les developpements/deploiements de suivre une architecture type :

### 1.a Toutes les sources sont dans /src, avec des sous-dossiers correspondant à des composants du projet
```
.                   # racine du projet
.src/                # repertoires des sources python/ipny/etc.
|__ composant/      # decoupage par composant (data/models/report/etc.)
    |__ file.py
|___composant_n/
    |___ file_n.py
```

### 1.b Tous les fichiers Dockerfile sont réparties dans des sous-dossier composants
```
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
```
### 1.c Example

Vous trouvez avec example, un exemple de composant, avec :

1. Un fichier docker-compose-example.yml
2. Un dossier src/example/ pour tous les fichiers sources python
3. Un dossier docker/example avec son fichier Dockerfile
   

## 2. Docker Compose - Gestion multi-services

### 2.1 Démarrer tous les services
```
docker compose up -d
```

### 2.2 Démarrer avec un docker-compose spécifique
```
docker compose -f docker-compose-data.yml up -d
```

> Cette ligne permet de lancer la creation de l'image spéfique, contenue dans le docker-compose-data.yml et de lancer son container.
> Cela permet donc d'isoler un composant particulier.
> 
> On pourra par la suite, dans un docker-compose.yml global au projet, y faire référence directement via le yml du composant (cf.dernièr partie).

### 2.3 Démarrer des services spécifiques (exemples courants)
```
docker compose up -d api mongodb mlflow-server postgres minio
docker compose up -d ml-worker
docker compose up -d airflow-webserver airflow-scheduler airflow-postgres
```
### 2.3 Démarrer des services spécifiques d'un composant spécifique
```
docker compose -f docker-compose-data.yml up -d extract transform
```

## 3. A savoir (Pour la culture, on passera par docker compose systématiquement pour combiner build et run)

### 3.1 Build et rebuild
```
docker compose build
```
### 3.2 build d'un service spécifique
```
docker compose build api
```
### 3.3 Forcer le build complet, sans vérification de cache
```
docker compose build --no-cache ml-worker
```

### 3.4 Gestion et maintenance
```
docker compose stop
docker compose stop api
docker compose restart api
docker compose down
docker compose down -v
docker compose exec api bash
docker compose exec ml-worker bash
docker compose logs -f api
docker compose logs -f ml-worker
```

### 3.5 Nettoyage
```
# Arrêter et supprimer le container
docker compose -f docker-compose-etl.yml down

# Supprimer l'image
docker rmi mlops-rakuten/clean-data:latest

# Nettoyer les images intermédiaires (builder stages)
docker image prune -f

# Nettoyer TOUT (containers arrêtés, images, volumes, cache)
docker system prune -a --volumes
```

## 🌐 URLs des services docker communs

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

## 4. Evolution dans la suite :

### 4.1 un Dockerfile optimisé !

> Pour faire un build puis un run, de façon à avoir un container optimisé avec uniquement les ressources nécessaires.
> Le container sera plus rapide à déployer et beaucoup plus rapide en execution.
> On construit une fois, on execute x fois !

```
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
```

> Les gains :

| Aspect            | Dockerfile Simple                    | Dockerfile Multi-stage          |
| ----------------- | ------------------------------------ | ------------------------------- |
| Taille image      | ~500-800 MB                          | ~150-250 MB                     |
| Contenu           | Python + dépendances + gcc + headers | Python + dépendances uniquement |
| Sécurité          | Outils de compilation présents       | Aucun outil de compilation      |
| Temps build       | Moyen                                | Légèrement plus long (2 stages) |
| Temps déploiement | Lent (image lourde)                  | Rapide (image légère)           |
| Cache Docker      | Efficace                             | Très efficace (layers séparés)  |

### 4.2 Fichier docker-compose global avec les include pour les docker-compose-composant.yml

```
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
```

> Bien plus simple non !