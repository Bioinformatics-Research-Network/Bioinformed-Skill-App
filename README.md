# Developer notes

![Build Status](https://github.com/Bioinformatics-Research-Network/Skill-cert-bot/workflows/tests/badge.svg) [![codecov](https://codecov.io/gh/Bioinformatics-Research-Network/Skill-cert-bot/branch/main/graph/badge.svg?token=MD2VSBJ141)](https://codecov.io/gh/Bioinformatics-Research-Network/Skill-cert-bot)

Primary maintainer: Henry Miller

This README contains notes to aid contributors and maintainers for this repo. It's a living document, so feel free to suggest changes any time. 


## Set up

```shell
smee -u https://smee.io/rSiwWHyU4AMt1zn --port 5000
```

```shell
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```



## Workflow for contributing:

All the work for this project has been modularized into relatively independent [issues](https://github.com/Bioinformatics-Research-Network/Skill-cert-bot/issues). If you see one which you would like to complete and it has no assignees, feel free to just add yourself as an assignee and get started. 

1. You are assigned an issue (or you self-assign)
2. Set up your dev environment using *** (this part needs to be figured out still)
3. Switch to your own branch (please do not work on the `main` branch unless you are the primary maintainer)
4. If developing new modules or functions, start by writing pytest unit tests in the `app/tests/` folder. It is good practice to write all unit tests prior to writing the modules which they test. That way, the expected behavior is clearly defined prior to writing the module code. 
5. Commit changes to your branch and push to github. It is recommended to do this at the end of a coding session to avoid potentially losing your progress.
6. Once your feature / module is ready, submit a pull request to pull your branch into `main`. The maintainer will review your code prior to merging it. 



