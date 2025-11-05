# 📦 Guide complet MLOps Rakuten - UV, Ruff, Git, Docker

---

## 1️⃣ Workflow quotidien avec UV et GIT

### -----------------------------
## COMMANDES PRINCIPALES
### 
### Démarrage matin (tous les jours)
### -----------------------------

#### On se met dans son projet
cd <mon_projet>

#### Partie Git
#### On rapatrie l'historique des changements du master
git fetch
# On bifurque sur la branche
git checkout <ma_branche> || git checkout -b <ma_branche> origin/<ma_branche>
# On met à jour avec le master distant
git pull --rebase origin master

#### Partie UV
#### !!!! A faire uniquement la première fois !!!!
uv venv

#### Démarrage de l'environnement virtuel uv
source .venv/bin/activate

#### Synchronisation avec toutes les dépendances
uv sync --extra all
### OU
#### Synchronisation partielle avec certaines dépendances uniquement
uv sync --extra api --extra database --extra monitoring

### -----------------------------

### -----------------------------
### Fin de journée (push pour PR)

#### Status pour voir tous les changements de la branche 
git status

#### Ajout de tous les fichiers modifiés à l'historique local (.) ou alors on précise les fichiers
git add .

####  On verrouille les modifications dans l'historique local
git commit -m "Mon avancement du jour sur <ma_branche>"

####  On rapatrie les modifications du master distant
git pull --rebase origin master

####  On pousse tous les changements sur la branche distante
git push -u origin <ma_branche>
### -----------------------------

### COMMANDES OPTIONNELLES SUR BESOIN

### Ajouter une dépendance (si besoin pendant le dev)
uv add <package>
git add pyproject.toml uv.lock
git commit -m "feat: ajoute <package>"

### Retirer une dépendance
uv remove <package>
git add pyproject.toml uv.lock
git commit -m "chore: retire <package>"


### Installation par groupes spécifiques (répéter --extra)
uv sync --extra api --extra database --extra monitoring
uv sync --extra datascience --extra database --extra mlflow-client
uv sync --extra airflow --extra database --extra mlflow-client

---

## 2️⃣ Qualité de code avec Ruff

### Workflow Ruff standard (avant chaque commit)
source .venv/bin/activate
ruff check . --fix
ruff format .
ruff check . --show-source

### Commandes individuelles
ruff check .
ruff check . --fix
ruff format .
ruff format . --check
ruff check . --show-source
ruff check . --quiet

---

## 3️⃣ Docker Compose - Gestion des services

### Commandes de base
docker compose build
docker compose pull
docker compose ps
docker compose logs -f
docker compose stats

### Démarrer avec un docker-compose spécifique
docker compose -f docker-compose-etl.yml up -d

### Démarrer tous les services
docker compose up -d

### Démarrer services spécifiques (exemples courants)
docker compose up -d api mongodb mlflow-server postgres minio
docker compose up -d ml-worker
docker compose up -d airflow-webserver airflow-scheduler airflow-postgres
docker compose up -d prometheus grafana

### Build et rebuild
docker compose build
docker compose build api
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

### Cas d'usage : dev ciblé (seulement quelques services)
docker compose up -d api mongodb mlflow-server postgres minio
docker compose up -d ml-worker

---

## 📝 Récapitulatif des commandes clés

### UV (dépendances)
| Commande | Usage |
|----------|-------|
| `uv venv` | Créer environnement virtuel |
| `uv sync --extra all` | Installer toutes les dépendances |
| `uv sync --extra api --extra database` | Installer groupes spécifiques (répéter --extra) |
| `uv add <package>` | Ajouter une dépendance |
| `uv remove <package>` | Retirer une dépendance |

### GIT (workflow quotidien)
| Commande | Usage |
|----------|-------|
| `git checkout <ma_branche>` | Basculer sur sa branche |
| `git pull --rebase origin master` | Mettre à jour depuis master |
| `git add . ; git commit ; git push` | Sauvegarder et pousser |

### RUFF (qualité)
| Commande | Usage |
|----------|-------|
| `ruff check . --fix` | Corriger automatiquement |
| `ruff format .` | Formater le code |
| `ruff check . --show-source` | Voir erreurs restantes |

### DOCKER (orchestration)
| Commande | Usage |
|----------|-------|
| `docker compose up -d` | Démarrer tous les services |
| `docker compose up -d api mongodb` | Démarrer services spécifiques |
| `docker compose logs -f <service>` | Voir logs en direct |
| `docker compose down -v` | Tout arrêter et reset |

---

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

---

## 💡 Astuces pratiques

- **TOUJOURS répéter `--extra` pour chaque groupe** : `uv sync --extra api --extra database`
- Toujours `ruff check . --fix && ruff format .` AVANT de committer
- Ne jamais oublier `git pull --rebase origin master` avant de commencer
- Docker Compose gère automatiquement les dépendances entre services (`depends_on`)
- Toujours travailler sur une branche spécifique, jamais sur `master`
- Les volumes Docker permettent de partager `./data/raw`, `./data/preprocessed`, `./data/processed` entre host et ml-worker


# Workflow Git collaboratif (branches/personne)

## Bonnes pratiques

- Chaque fonctionnalité, correction ou tâche doit être développée sur une branche dédiée.
- Nommez vos branches de façon descriptive : ex. `feature/login`, `fix/bug-auth`.
- Ne jamais développer ou valider directement sur `master`. Toujours utiliser une branche dédiée.
- Avant fusion, assurez-vous que votre branche est à jour avec les dernières modifications de `master`.
- Demander une relecture (pull request/MR) avant toute fusion dans `master`.
- Une fois la branche fusionnée, supprimez-la pour garder le dépôt propre.

## Différence entre `master` et `origin/master`

- `master` : branche principale locale.
- `origin/master` : copie de la principale distante (serveur). Mise à jour par `git fetch` ou `git pull`.

## Commandes type à utiliser

### Récupérer les dernières modifications du dépôt distant
git fetch origin

### Créer une branche à partir de master
git checkout master
git pull origin master
git checkout -b nom_branche

### Travailler, puis préparer le commit
git add .
git commit -m "Message descriptif du changement"

### Pousser la branche sur le dépôt distant
git push origin nom_branche

### Mettre à jour la branche de travail avec master si besoin
git fetch origin
git merge origin/master

### Une fois que tout est prêt, fusionner la branche dans master
git checkout master
git pull origin master
git merge nom_branche

### Envoyer la nouvelle version de master sur le serveur
git push origin master

### Supprimer la branche localement (après fusion)
git branch -d nom_branche

### Voir la différence entre votre master locale et celle du serveur
git diff master origin/master

## Résumé du workflow

1. Créer une branche dédiée à ta tâche.
2. Travailler (commits, push) uniquement sur ta branche.
3. Avant la fusion, synchroniser ta branche avec l’avancement sur master : `git merge origin/master`.
4. Fusionner la branche via une Pull/Merge Request ou depuis le terminal.
5. Supprimer ta branche après fusion.
6. Répéter pour chaque nouvelle tâche/fonctionnalité.

---
Ce workflow améliore la lisibilité, facilite la collaboration et réduit les conflits lors du travail en équipe sur un projet Git.

# Résumé des commandes git suite à la PR
### Sur sa branche
git checkout <branch_prenom>
# Mise à jour historique des changements distants
git fetch origin
# Branchement sur master
git checkout master
# # On realigne local/distant du master
git pull origin master
# On rebascule sur sa branche
git checkout branch_sebastien
# On realigne local/distant
git pull --rebase origin master
