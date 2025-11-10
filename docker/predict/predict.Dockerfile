# ==========================================================
# 🐳 Dockerfile — Service de prédiction XGBoost Rakuten
# ==========================================================

FROM python:3.11-slim

# Répertoire de travail à l'intérieur du conteneur
WORKDIR /app

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 && rm -rf /var/lib/apt/lists/*

# Copier uniquement les fichiers nécessaires
COPY requirements-predict.txt .
RUN pip install --no-cache-dir -r requirements-predict.txt

# Copier le code source
COPY src ./src

# Créer les dossiers montés pour data et modèles
RUN mkdir -p /app/data /app/mlruns

# Variables d’environnement
ENV PYTHONPATH=/app/src

# Commande par défaut : prédiction simple
CMD ["python", "-m", "api.predict"]
