# Developer notes

![Build Status](https://github.com/Bioinformatics-Research-Network/BRN-bot/workflows/tests/badge.svg) [![codecov](https://codecov.io/gh/Bioinformatics-Research-Network/BRN-bot/branch/main/graph/badge.svg?token=64FAWBD72C)](https://codecov.io/gh/Bioinformatics-Research-Network/BRN-bot)

Primary maintainer: Henry Miller

This README contains notes to aid contributors and maintainers for this repo. It's a living document, so feel free to suggest changes any time. 

## Dev notes

### Quick start

Here are the steps required for setting up and launching the BRN bot

1. Clone repo

```shell
git clone git@github.com:Bioinformatics-Research-Network/BRN-bot.git
```

2. Switch to your branch (do not commit / push to main)

```shell
git checkout -b <name_of_branch>
```

3. Install nodejs & smee

```shell
curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh
sudo bash /tmp/nodesource_setup.sh
sudo apt install nodejs
sudo npm install -g smee-client
```

4. Start smee channel

```shell
smee -u https://smee.io/rSiwWHyU4AMt1zn --port 8001
```

5. Install python deps & launch env

```shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
poetry install
```

6. Set environmental variables (ask Henry for these)

```shell
export APP_ID="******"
export BOT_KEY_PATH="/path/to/bot/key.pem"
```

7. Activate poetry env

```shell
poetry shell
```

8. Run unit tests

```shell
pytest
```

9. Launch the app

```shell
uvicorn main:app --reload --port 8001
```

10. Try it out by navigating to the [test repo PR](https://github.com/Bioinformatics-Research-Network/test-bot/pull/1) and writing "@brnbot hello" in the PR comments. You should see a response from BRN bot which says "Hello <your_gh_username>! 😊". For a list of all available commands, type "@brnbot help".


### Other notes and considerations

1. You can add new deps to the poetry env by running `poetry add <package_name>`
2. The app must be installed by GitHub organizations to be used. As each skill assessment has its own organization (e.g., Python Programming II), the bot has to be installed separately for each. After this is done, the *Install ID* must be registered in `bot/const.py` within the `installation_ids` object. You can obtain the installation ID for an organization by commenting on a PR/Issue in that org and getting the [webhook output from smee.io](https://smee.io/rSiwWHyU4AMt1zn) -- the install ID is in the event payload under `{"installation": {"id": <id_number>}}`


## Workflow for contributing:

All the work for this project has been modularized into relatively independent [issues](https://github.com/Bioinformatics-Research-Network/Skill-cert-bot/issues). If you see one which you would like to complete and it has no assignees, feel free to just add yourself as an assignee and get started. 

1. You are assigned an issue (or you self-assign)
2. Set up your dev environment using *** (this part needs to be figured out still)
3. Switch to your own branch (please do not work on the `main` branch unless you are the primary maintainer)
4. If developing new modules or functions, start by writing pytest unit tests in the `tests/` folder. It is good practice to write all unit tests prior to writing the modules which they test. That way, the expected behavior is clearly defined prior to writing the module code. 
5. Commit changes to your branch and push to github. It is recommended to do this at the end of a coding session to avoid potentially losing your progress.
6. Once your feature / module is ready, submit a pull request to pull your branch into `main`. The maintainer will review your code prior to merging it. 



