# Developer notes

![Build Status](https://github.com/Bioinformatics-Research-Network/Skill-cert-API/workflows/tests/badge.svg) [![codecov](https://codecov.io/gh/Bioinformatics-Research-Network/Skill-cert-API/branch/main/graph/badge.svg?token=MD2VSBJ141)](https://codecov.io/gh/Bioinformatics-Research-Network/Skill-cert-API)

Primary maintainer: Anmol Singh ([itchytummy](https://github.com/itchytummy))

This README contains notes to aid contributors and maintainers for this repo. It's a living document, so feel free to suggest changes any time. 

## Workflow for contributing:

All the work for this project has been modularized into relatively independent [issues](https://github.com/Bioinformatics-Research-Network/Skill-cert-API/issues). If you see one which you would like to complete and it has no assignees, feel free to just add yourself as an assignee and get started. 

1. You are assigned an issue (or you self-assign)
2. Set up your dev environment using [gitpod](https://www.gitpod.io/) (preferred) or locally using the steps in the description [below](#setting-up-the-dev-environment-non-gitpod).
3. Switch to your own branch (please do not work on the `main` branch unless you are the primary maintainer)
4. If developing new modules or functions, start by writing pytest unit tests in the `app/tests/` folder. It is good practice to write all unit tests prior to writing the modules which they test. That way, the expected behavior is clearly defined prior to writing the module code. 
5. Commit changes to your branch and push to github. It is recommended to do this at the end of a coding session to avoid potentially losing your progress.
6. Once your feature / module is ready, submit a pull request to pull your branch into `main`. The maintainer will review your code prior to merging it. 

## Henry's notes and suggestions for contributors

From Henry, here are some suggestions for contributors to follow:

I found a really great example of a similar FastAPI CRUD app [here](https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app). I have set up the repo to follow their format and I think we should try to stick to it. The example comes from the person who created FastAPI, so it is pretty solid.

Other notes:

1. **Before you start building your python modules, please write your unit tests in pytest**. API functions, CRUD functions, and bot functions should have a unit test. Ideally we would hit > 90% code coverage for the whole app. FastAPI + Pytest docs: https://fastapi.tiangolo.com/tutorial/testing/ Writing unit tests prior to development will (1) force you to think through what you are building and what you expect it to do, (2) allows you to rapidly/automatically test your code as you build it, (3) allow others to figure out how you expect your modules to work (for compatibility with their modules) and identify unmet dependencies from their modules in your codebase. Here is a really beautiful example of incorporating pytest unit tests into a FastAPI CRUD app: https://github.com/tiangolo/full-stack-fastapi-postgresql/tree/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/tests
2. **Please never push to the main branch**, use your own branch and submit a pull-request. Also **please do not merge your own PR** unless you are the maintainer.
3. **Document your code** (docstrings for functions, comments).
4. **Use accepted pythonic coding practices** - try to keep your code style simple, PEP-compliant, and don't repeat yourself (DRY) where possible. Run `black` to automatically format your code prior to submitting the PR:

```shell
black app/
```

5. **Ask for feedback any time** -- no one is an expert here so if you have any doubts or questions, just let us know and we can all figure it out together!
6. As a pro-tip, **try using gitpod for your IDE** (it's VS Code in your browser with pre-built dev environments). I use it and I found it makes life way easier since you are in the same dev environment as everyone else.


## Setting up the dev environment (non-gitpod)

These steps will detail how to set up the dev environment and get started. 

**NOTE:** If you are using gitpod (recommended), you will not need to perform any of the following steps -- just click the "gitpod" button in GitHub on this repo and the dev env will be built automatically.

1. Clone repo

```shell
git clone git@github.com:Bioinformatics-Research-Network/Skill-cert-API.git
```

2. Switch to your branch (do not commit / push to main)

```shell
git checkout -b <name_of_branch>
```

3. Install poetry

```shell
curl -sSL https://install.python-poetry.org | python3 -
```

4. Install deps with `poetry`

```shell
export PATH="$HOME/.local/bin/poetry:$PATH"
poetry install
```

You might encounter a `ModuleNotFoundError` in this step -- if so, see the solution [here](https://stackoverflow.com/questions/71086270/no-module-named-virtualenv-activation-xonsh).


5. Source the poetry env

```shell
poetry shell
```

6. Set environmental variables

```shell
export BADGR_TEST_USERNAME="**************"
export BADGR_TEST_PASSWORD="**************"
export MANDRILL_API_KEY="**************"
```

7. Install and configure AWS CLI

```shell
conda install -c conda-forge aws-cli
aws configure --profile brn
```

8. AWS sync with `skill-assessment-app/` bucket to a local folder `s3_data/`

```shell
aws s3 --profile brn sync s3://skill-assessment-app s3_data/
```

9. Run unit tests:

```shell
pytest
```

## Run API locally

1. Run the following command to create and fill the database.

```shell
python app/db/fill_db.py
```

2. Install smee client (and NodeJS) to recieve event payloads from registration form

```shell
curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh
sudo bash /tmp/nodesource_setup.sh
sudo apt install nodejs
sudo npm install -g smee-client
```

4. In a separate terminal, start the app using `uvicorn`:

```shell
uvicorn main:app --reload --port 2000
```

To test out the API locally use the Swagger UI docs:

Open your prefered web browser and enter following URL `http://127.0.0.1:8000/docs`. This will help you in discovering how to use the API.

To learn more about basics of FastAPI: https://fastapi.tiangolo.com/tutorial/first-steps/