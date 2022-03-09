# Developer notes

## Getting started

These steps will detail how to set up the dev environment and get started. **NOTE:** If you are using gitpod (recommended), you will not need to perform any of the following steps.

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
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

4. Install app developer deps with `poetry`

```shell
source $HOME/.poetry/env
poetry install
```

You might encounter a `ModuleNotFoundError` in this step -- if so, see the solution [here](https://stackoverflow.com/questions/71086270/no-module-named-virtualenv-activation-xonsh).



