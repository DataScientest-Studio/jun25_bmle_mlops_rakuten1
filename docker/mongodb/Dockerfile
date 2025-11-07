# Image officielle MongoDB version 7.x
FROM mongo:7

# Copie la configuration MongoDB personnalisée (depuis le répertoire conf du projet)
COPY conf/mongodb.yaml /etc/mongod.conf

# (Optionnel) S’assure que le dossier des logs existe et appartient à l’utilisateur MongoDB
RUN mkdir -p /var/log/mongodb && chown -R mongodb:mongodb /var/log/mongodb

# Démarre mongod en utilisant le fichier de configuration personnalisé
CMD ["mongod", "--config", "/etc/mongod.conf"]
