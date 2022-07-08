# *Bioinformed* Skill Assessment Platform

[![Support: BioResNet](https://img.shields.io/badge/Support-BioResNet-purple.svg)](https://www.bioresnet.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](https://opensource.org/licenses/MIT)
[![Contributions: Welcome](https://img.shields.io/badge/Contributions-Welcome-forestgreen.svg)](#dev-guide)
[![Code: of conduct](https://img.shields.io/badge/Code-Of%20Conduct-blue.svg)](https://docs.google.com/document/d/1q06RJbIsyIzLC828A7rBEhtfkujkj9kx7Y118AaWASA/edit)


[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/Bioinformatics-Research-Network/Bioinformed-Skill-App)


### Table of contents

- [Overview](#overview)
- [Dev guide](#dev-guide)
  * [Contributing](#contributing)
    + [Issues](#issues)
    + [Standards](#standards)
    + [CODEOWNERS](#codeowners)
    + [Code of Conduct](#code-of-conduct)
  * [Dev environment](#dev-environment)
    + [Spinning up a local copy of the prod env](#spinning-up-a-local-copy-of-the-prod-env)
      - [Example with WebUI service](#example-with-webui-service)
    + [ENV variables and security](#env-variables-and-security)
    + [Rebuilding database](#rebuilding-database)
    + [Setting up the dev environment (non-gitpod)](#setting-up-the-dev-environment--non-gitpod-)
  * [Testing and coverage](#testing-and-coverage)
  * [GitHub actions](#github-actions)
    + [Badges for unit tests and coverage](#badges-for-unit-tests-and-coverage)

## Overview

The *Bioinformed* Skill Assessment Platform enables users to complete BRN skill assessments, earn badges, and demonstrate their skills to potential partners and employers.

This app is developed collaboratively by the Bioinformatics Research Network Infrastructure WG. 

It comprises **six services** which correspond to the directories in this repo:

1. `webui`
    - A [flask](https://flask.palletsprojects.com/en/2.1.x/) application for serving the web UI to the users. This enables the user to authenticate with the app, see/edit their info, find assessments, launch assessments, and view their badges. The `webui/` directory contains the code for that part of the app.
2. `ghbot`
    - A [GitHub app](https://docs.github.com/en/developers/apps) + [FastAPI](https://fastapi.tiangolo.com/) gateway for managing user interactions on GitHub and performing operations required to enable the app features. It is located in the `ghbot/` directory.
3. `slackbot`
    - A [Slack App](https://api.slack.com/start/building) + [FastAPI](https://fastapi.tiangolo.com/) gateway for managing user interactions on Slack, similar to the GitHub app. It is located in the `slackbot/` directory.
4. `crud` 
    - A CRUD app + [FastAPI](https://fastapi.tiangolo.com/) gateway for responding to requests from all other services, updating the database, and returning data to the requesting services. This is the hub of the platform and it also serves to enforce security standards by preventing unauthorized access to the back-end database. It is located in the `crud/` directory.
5. `db`
    - An [AWS RDS](https://aws.amazon.com/rds/) MySQL database which holds the data necessary for the platform. 
6. `sync`
    - An [AWS Lambda](https://aws.amazon.com/lambda/) function for synchronizing all data sources used by the app. It is located in the `sync/` directory.

**Overview diagram**:

![](https://lucid.app/publicSegments/view/4c2784e9-45ce-4f69-ba17-7bd9e8d74261/image.png)

## Dev guide

For a quickstart watch the first 20 min of this project's [video dev notes](https://www.loom.com/share/10fc59eaeb1b47af8293ac83e9be3bac). The instructions in that video and in the following documentation apply to all services in the app. For additional details, see the `README.md` within each service's directory.

### Contributing

The **workflow for contributing**:

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

Anyone can assign themselves to an issue. If we need someone else to work on it instead, then someone will **politely** ask you to give up the issue.

#### Standards

To keep this project neat, organized, and easy to contribute to, please make sure to do all the following when writing new code:

1. Lint / Style your code
    - We use [flake8](https://flake8.pycqa.org/en/latest/) for linting.
    - Run `flake8 .` and fix all warnings / errors
    - Run `black -l 80 --experimental-string-processing .` to automatically style your code (the `-l 80 --experimental-string-processing` part wraps long lines).
2. Write unit tests for new features / functions
    - New features and functions should be covered by unit tests when possible.
3. Document your code
    - Use [docstrings](https://peps.python.org/pep-0257/) to document your functions. Please be descriptive so that others can follow / understand your code.
    - Use comments to describe your code within function
    - If your code introduces new user behaviors, open an issue for the `webui` so they can be appropriately documented in the user interface
    - If your code introduces new developer requirements, update the `README.md` files appropriately
4. Try to follow principles like [YAGNI, KISS, and DRY](https://henriquesd.medium.com/dry-kiss-yagni-principles-1ce09d9c601f) when practical to do so
    - DRY (don't repeat yourself) 
    - KISS (keep it simple, stupid)
    - YAGNI (you ain't gonna need it)

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

#### Code of Conduct

At all times, contributors are expected to abide by the [BRN Code of Conduct](https://docs.google.com/document/d/1q06RJbIsyIzLC828A7rBEhtfkujkj9kx7Y118AaWASA/edit). Failure to follow these guidelines may result in discplinary action, such as a ban from contributing to this work.

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

Then you can proceed to work on `<my_service>` as desired.

##### Example with WebUI service

For example, if you wanted to work on the webui, launch the following:

```shell
docker-compose up --build --scale webui=0
```

From this point onwards, you can use a separate terminal to work on the webui service:

```shell
# Set up environment for local development on webui
export APP_ENV=testing
cd webui/
pip install -r requirements.txt

# Launch webui app (use 9630 because this is what docker compose uses)
flask run -p 9630 --reload --debugger
```

If you are working remotely, you will need to forward port 9630 (use the port panel in VS Code to do this, for example) -- then you should be able to navigate to http://localhost:9630 in your browser and see the app running.

#### ENV variables and security

All secrets and environmental variables are stored in `.env` files which are loaded into the dev env automatically (if using gitpod). You must have AWS access in order to obtain them -- as @millerh1 if you need this. We use [pydantic[dotenv]](https://pydantic-docs.helpmanual.io/usage/settings/) to load them for each app based on the `APP_ENV` environmental parameter.

```shell
# App will use .test.env
export APP_ENV=testing

...

# App will use .dev.env
export APP_ENV=development
```

While working locally on a particular service, always use the `testing` env. This will ensure that the service you are working on can correctly network with the other services running in docker-compose. By default, all services in docker-compose will use the `development` env.

All `.env` files should be treated as **strictly confidential**. They should never be shared or pushed to GitHub. By default, the `.gitignore` file will ignore these -- but still be careful that you do not accidentally overwrite the `.gitignore`.

Environmental variables, ssh keys, OAuth tokens, or other secrets should never be committed to the git history or otherwise stored in plain text anywhere. 

For secrets needed during the dev process, store them in gitpod as user variables (preferred), or simply export them in your local terminal:

```shell
export MY_SECRET=<my_secret_value>
```

For secrets needed during GitHub actions, notify @millerh1 and he can add them.

Finally, if you notice any secrets/keys in the git repo, notify @millerh1 immediately via Slack (BRN members) or via [email](henry@bioresnet.org) (outside contributors).

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

#### Setting up the dev environment (non-gitpod)

These steps will detail how to set up the dev environment and get started without using gitpod.

1. Clone repo

```shell
git clone git@github.com:Bioinformatics-Research-Network/Bioinformed-Skill-App.git
```

2. Switch to your branch

```shell
git checkout -b <name_of_branch>
```

3. Install AWS CLI

```shell
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install -i /usr/local/aws-cli -b /usr/local/bin
rm -r aws/
rm awscliv2.zip
```

4. Configure AWS CLI with your access credentials (also set default region to `us-east-1`)

```shell
aws configure
```

5. Get the .env files for all services in the app

```shell
aws s3 cp s3://skill-assessment-app/dev-secrets/.env.download.dev.sh .
bash .env.download.dev.sh
```

6. Install python 3.10.4 using [pyenv](https://github.com/pyenv/pyenv)

```shell
pyenv install 3.10.4
pyenv shell 3.10.4  # Activate pyenv
```

7. Create venv

```shell
python -m venv venv
```

8. Install global deps

```shell
pip install -r requirements.txt
```

9. Install service specific deps:

```shell
cd <service_dir>/
pip install -r requirements.txt
```

10. Set environmental variables

```shell
export APP_ENV="testing"
```

11. In a new & separate terminal, spin up docker-compose (excluding the service you want to develop for)

```shell
docker-compose up --scale <service>=0
```

### Testing and coverage

We use unit tests to ensure the code works as expected, even after new features are added or bugs squashed. Because all the repos are python-based, we use the [pytest](https://docs.pytest.org/en/6.2.x/index.html) unit testing system. Within the directory for each service is a `tests/` folder -- this contains the tests. You can learn more about writing and running tests from the official pytest docs [here](https://docs.pytest.org/en/6.2.x/index.html).

To run tests, simply navigate to the service of interest, and run `pytest`:

```shell
# Enter webui/ dir
cd webui/

# Install service deps if you haven't already
pip install -r requirements.txt

# Set app env
export APP_ENV=testing

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

# Set app env
export APP_ENV=testing

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

