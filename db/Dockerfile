FROM mysql:8.0

ARG MYSQL_PROD_HOST
ARG MYSQL_PROD_USER
ARG MYSQL_PROD_PASSWORD
ARG MYSQL_PROD_DATABASE

ENV MYSQL_PROD_HOST ${MYSQL_PROD_HOST}
ENV MYSQL_PROD_USER ${MYSQL_PROD_USER}
ENV MYSQL_PROD_PASSWORD ${MYSQL_PROD_PASSWORD}
ENV MYSQL_PROD_DATABASE ${MYSQL_PROD_DATABASE}

WORKDIR /db

# Dump the production database to a file for importing into the development database
RUN echo "CREATE DATABASE IF NOT EXISTS $MYSQL_PROD_DATABASE; USE $MYSQL_PROD_DATABASE;" > /docker-entrypoint-initdb.d/db.sql
RUN mysqldump --no-tablespaces -h $MYSQL_PROD_HOST -u $MYSQL_PROD_USER -p$MYSQL_PROD_PASSWORD $MYSQL_PROD_DATABASE >> /docker-entrypoint-initdb.d/db.sql

EXPOSE 3306
