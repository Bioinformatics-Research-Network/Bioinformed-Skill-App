# Bioinformed-Skill-App

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App)


Repository for the Bioinformed Skill Assessment App

## Overview

The purpose of this app is to enable users to complete BRN skill assessments. 

It contains six components:

1. A [flask](https://flask.palletsprojects.com/en/2.1.x/) application for serving the web UI to the users. This enables the user to authenticate with the app, see/edit their info, find assessments, launch assessments, and view their badges. The `webui/` directory contains the code for that part of the app.
2. A GitHub app + FastAPI gateway for managing user interactions on GitHub and performing operations required to enable the app features. It is located in the `ghbot/` directory.
3. A Slack App + FastAPI gateway for managing user interactions on Slack, similar to the GitHub app. It is located in the `slackbot/` directory.
4. A CRUD app + FastAPI gateway for responding to requests from all other services, updating the database, and returning data to the requesting services. This is the hub of the platform and it also serves to enforce security standards by preventing unauthorized access to the back-end database. It is located in the `crud/` directory.
5. A MySQL database which holds the data necessary for the platform. 
6. An [AWS Lambda](https://aws.amazon.com/lambda/) function for synchronizing all data sources used by the app. It is located in the `sync/` directory.

## Dev environment

The ideal environment for developing this app is [gitpod](https://gitpod.io/). You can launch that environment by creating a gitpod account, defining your AWS credentials in your user variables, and then clicking the "Open in Gitpod" button (above).

To launch the dev environment, follow the quickstart video [here](https://www.loom.com/share/10fc59eaeb1b47af8293ac83e9be3bac) (just the first 20 minutes).


Finally, the dev environment is defined by `.gitpod.yml` -- and if you wish to develop without gitpod, you are encouraged to repeat the steps in the `.gitpod.yml` file locally so that you can faithfully reproduce the dev environment. 

### Development workflow

**Note**: These instructions apply broadly to all services in the app. For additional details, see the `README.md` within each directory.

To spin up all services and create a copy of the production environment in gitpod (or your local computer), simply run the following:

```shell
docker-compose up
```

If you want to work on a particular service (e.g., the CRUD app), spin up all other services except the one you want to work on:

```shell
docker-compose up --scale <my_service>=0
```

For example, if you wanted to work on the webui:

```shell
docker-compose up --build --scale webui=0
```

This will cause all other services to launch except the web application.

#### Rebuilding database

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
