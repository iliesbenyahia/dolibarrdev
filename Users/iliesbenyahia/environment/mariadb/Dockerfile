# Utilisez l'image officielle MariaDB comme image de base
FROM mariadb:10.3



# Créez un répertoire dans le conteneur où vous pourrez monter des fichiers depuis l'hôte
#RUN mkdir /docker-entrypoint-initdb.d

# Copiez des scripts SQL personnalisés dans le répertoire d'initialisation du conteneur
#COPY ./your_sql_script.sql /docker-entrypoint-initdb.d/

# Vous pouvez également personnaliser d'autres configurations ici si nécessaire

# Exposez le port par défaut de MariaDB (3306)
EXPOSE 3306

# Commande d'initialisation par défaut pour le conteneur MariaDB
CMD ["mysqld"]
