# Bioinformed-Skill-App

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App)


Minor update

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

