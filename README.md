# Bioinformed-Skill-App

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App)


Repository for the Bioinformed Skill Assessment App

## Dev environment

The dev environment is defined by `.gitpod.yml` and `docker-compose.yml`. 

### Using `docker-compose.yml`

The easiest way to spin up the dev environment is to start all services except the one you want to work on:

```shell
docker-compose up --build --scale <my_service>=0
```

For example, if you wanted to work on the web app:

```shell
docker-compose up --build --scale webui=0
```

This will cause all other services to launch except the web application.

#### Debuilding database

Sometimes it is necessary for us to rebuild the local version of the db. This need might arise if the local database is altered and no longer works (as in deleting necessary tables/records), or if the production database changes and the new data is required for local testing.

To resync the local database with production, do the following:

1. Stop the running db service

```shell
docker-compose down
```

2. Rebuild the db docker image with the correct data

```shell
docker-compose build --no-cache db
```

3. Restart the services using the updated data

```shell
docker-compose up --build --force-recreate --no-deps
```

This should spin up the db with a full copy of the current prod database.
