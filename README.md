# *Bioinformed* Skill Assessment Platform

[![Support: BioResNet](https://img.shields.io/badge/Support-BioResNet-purple.svg)](https://www.bioresnet.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)
[![Contributions: Welcome](https://img.shields.io/badge/Contributions-Welcome-green.svg)](#dev-guide)


[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App)


## Overview

The purpose of this app is to enable users to complete BRN skill assessments. 

It contains **six services**:

1. `webui`
  - A [flask](https://flask.palletsprojects.com/en/2.1.x/) application for serving the web UI to the users. This enables the user to authenticate with the app, see/edit their info, find assessments, launch assessments, and view their badges. The `webui/` directory contains the code for that part of the app.
2. `ghbot`
  - A GitHub app + FastAPI gateway for managing user interactions on GitHub and performing operations required to enable the app features. It is located in the `ghbot/` directory.
3. `slackbot`
  - A Slack App + FastAPI gateway for managing user interactions on Slack, similar to the GitHub app. It is located in the `slackbot/` directory.
4. `crud` 
  - A CRUD app + FastAPI gateway for responding to requests from all other services, updating the database, and returning data to the requesting services. This is the hub of the platform and it also serves to enforce security standards by preventing unauthorized access to the back-end database. It is located in the `crud/` directory.
5. `db`
  - A MySQL database which holds the data necessary for the platform. 
6. `sync`
  - An [AWS Lambda](https://aws.amazon.com/lambda/) function for synchronizing all data sources used by the app. It is located in the `sync/` directory.

**Overview diagram**:

![](https://lucid.app/publicSegments/view/4c2784e9-45ce-4f69-ba17-7bd9e8d74261/image.png)

## Dev guide

For a quickstart watch the first 20 min of this project's [video dev notes](https://www.loom.com/share/10fc59eaeb1b47af8293ac83e9be3bac). The instructions in that video and in the following documentation apply to all services in the app. For additional details, see the `README.md` within each service directory.

### Contributing

The workflow for contributing is as follows:

1. Assign yourself to an issue.
2. Create a new branch for this issue (or fork the repo if you are not in BRN).
3. Work on the code and complete the requirements of the issue. Please write descriptive commit messages!
4. Test your code locally to make sure it is working. 
  - Make sure any new features are covered by unit tests. 
  - Run `black .` to style your code before final push to github.
5. Submit a pull request (PR) to add your changes to the `main` branch. 
6. Respond to reviewer critiques until the PR is merged. 

#### Issues

To keep things organized, the contribution workflow will begin with [issues](https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App/issues). 

If you want a new feature, if you want a bug fixed, or some other change in the code, begin by [opening an issue](https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App/issues/new). Describe what changes you want, try to be as detailed as possible. If there's a bug, describe how to replicate the bug (preferrably in gitpod). If you want a feature, describe why you want this feature and provide details on what it will take to create it (if you already have an idea). 

New issues should also be labeled so we know what kind of issue it is, and what service it pertains to -- see examples [here](https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App/issues). 

Once a new issue is created, it will go onto the [project board](https://github.com/orgs/Bioinformatics-Research-Network/projects/1). If something is high urgency it will go into "Todo". If it is low urgency, it should go in the "Backlog". 

Anyone can assign themselves to an issue. If, for some reason, we need someone else to work on it instead, then someone will politely ask you to either share if you've already started work, or give up the issue if you haven't started yet.

#### CODEOWNERS

BRN uses [branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches) for the `main` branch. This means that only authorized accounts can add to this branch directly without submitting a pull request.

The `CODEOWNERS` file describes these roles:

```CODEOWNERS
/crud        @itchytummy
/webui       @millerh1
/sync        @millerh1
/db          @millerh1
/slackbot    @jmsdao @millerh1
/*           @millerh1  # Files in root dir
/.github     @millerh1
```

For example, the line `/crud    @itchytummy` indicates that only @itchytummy can push commits to `main` if they include changes in the `crud/` dir.

### Dev environment

The ideal environment for developing this app is [gitpod](https://gitpod.io/). You can launch that environment by creating a gitpod account, defining your AWS credentials in your user variables (watch video to see how to do this), and then click the "Open in Gitpod" button (above).

The gitpod dev environment is defined by `.gitpod.yml` -- and if you wish to develop without gitpod, you are encouraged to repeat the steps in the `.gitpod.yml` file locally so that you can faithfully reproduce the dev environment. 

#### Spinning up a local copy of the prod env

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

### Testing and coverage

We use unit tests to ensure the code works as expected, even after new features are added or bugs squashed. Because all the repos are python-based, we use the [pytest](https://docs.pytest.org/en/6.2.x/index.html) unit testing system. Within the directory for each service is a `tests/` folder -- this contains the tests. You can learn more about writing and running tests from the official pytest docs [here](https://docs.pytest.org/en/6.2.x/index.html).

To run tests, simply navigate to the service of interest, and run `pytest`:

```shell
# Enter webui/ dir
cd webui/

# Install service deps if you haven't already
pip install -r requirements.txt

# Run pytest
pytest
```

**Note**: All other services will have to be running for this to work (see docker-compose instructions above).

Finally, we use 'coverage' to measure the proportion of the code base which our `tests/` actually test.

You can locally test coverage by running the following:

```shell
# Enter webui/ dir
cd webui/

# Install service deps if you haven't already
pip install -r requirements.txt

# Run pytest via coverage
coverage run -m pytest

# Report the coverage
coverage report
```

This will indicate the proportion of the codebase covered by the tests. To explore which lines are not covered, export an HTML report, download it, and then open it in your browser:

```shell
coverage html  # Run this after `coverage run -m pytest`
```

### GitHub actions

To automate the process of unit tests, code coverage, and deployment, we use [GitHub actions](https://github.com/features/actions). We create workflows (found in the `.github/workflows/` dir) which use YAML to define all the steps run in GitHub actions. 

For each service, there are two workflows currently defined:

1. `test.<service>.yml` - runs unit tests and code coverage. 
  - This is triggered anytime a chance is made on the `main` branch in the directory for that service OR whenever a pull request is made to add changes to the main branch for that service. 
  - If it fails, see the output on the [actions tab](https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App/actions) and try to fix what went wrong. 
  - If you need help, just let @millerh1 know!
2. `deploy.<service>.yml` - deploys the service into production on AWS. 
  - This is only triggered manually by @millerh1.

Most of these files are boilerplate, so you will not need to edit/write them yourself unless you want to!

#### Badges for unit tests and coverage

In each repo, there are two badges which are automatically updated by GitHub actions:

[![Test CRUD](https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App/actions/workflows/test.crud.yml/badge.svg)](https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App/actions/workflows/test.crud.yml) [![codecov](https://codecov.io/gh/Bioinformatics-Research-Network/Bioinformed-Skill-App/branch/main/graph/badge.svg?flag=crud)](https://codecov.io/gh/Bioinformatics-Research-Network/Bioinformed-Skill-App)

These badges come from running unit tests and code coverage as part of the GitHub actions workflow for that directory. 

